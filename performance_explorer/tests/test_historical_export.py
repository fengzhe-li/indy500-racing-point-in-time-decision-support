import unittest
from copy import deepcopy
from performance_explorer.scripts.export_historical import build, exclusion, read, CANONICAL, artifacts, ROOT

class HistoricalExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.audit, cls.ledger = build()
        cls.attempts = read(CANONICAL / 'attempts.csv')
        cls.laps = read(CANONICAL / 'attempt_laps.csv')

    def test_year_population_and_old_export_regression(self):
        self.assertEqual([46,50,39,30,31], [r['retained_rows'] for r in self.audit['years']])
        self.assertEqual([46,51,40,69,54], [r['v5_complete'] for r in self.audit['years']])
        self.assertEqual([46,50,39,30,3], [r['old_explorer'] for r in self.audit['years']])
        self.assertEqual(196, len(self.data['rows']))
        for r in self.audit['years']:
            self.assertEqual(r['source_rows'], r['retained_rows']+r['excluded_rows'])
            self.assertEqual(r['excluded_rows'],sum(r['exclusions'].values()))

    def test_unknown_attempt_order_is_nullable_not_invented(self):
        recovered = [r for r in self.data['rows'] if r['year']==2024 and r['attempt'] is None]
        self.assertEqual(28, len(recovered))
        self.assertEqual(28, len({r['attemptId'] for r in recovered}))
        self.assertTrue(all(len(r['lapTimesS'])==4 for r in recovered))

    def test_no_validity_policy_relaxation(self):
        self.assertTrue(all(r['resultStatus']=='VALID_RETAINED' for r in self.data['rows']))
        self.assertTrue(all(not r['retained'] for r in self.ledger if r['result_status']!='VALID_RETAINED'))

    def test_duplicate_missing_invalid_laps_are_rejected(self):
        a = next(a for a in self.attempts if a['result_status']=='VALID_RETAINED')
        laps = [l for l in self.laps if l['attempt_id']==a['attempt_id']]
        self.assertIsNone(exclusion(a,laps))
        self.assertEqual('missing_or_duplicate_lap_number',exclusion(a,laps[:-1]))
        self.assertEqual('missing_or_duplicate_lap_number',exclusion(a,laps[:-1]+[laps[0]]))
        for value in ['0','-1','nan','inf','']:
            bad=deepcopy(laps);bad[0]['lap_time_seconds']=value
            self.assertEqual('invalid_lap_timing',exclusion(a,bad))
        bad=deepcopy(laps);bad[0]['lap_time_seconds']='10'
        self.assertEqual('inconsistent_total_time',exclusion(a,bad))
        bad=dict(a);bad['four_lap_total_seconds']='nan'
        self.assertEqual('invalid_aggregate_timing',exclusion(bad,laps))
        bad=dict(a);bad['car_attempt_index']=''
        self.assertIsNone(exclusion(bad,laps))

    def test_timing_consistency_and_provenance(self):
        self.assertLess(self.audit['max_time_sum_error_s'], 1e-10)
        self.assertEqual(0,self.audit['orphan_laps'])
        for r in self.data['rows']:
            self.assertAlmostEqual(r['totalSeconds'], sum(r['lapTimesS']), places=9)
            self.assertEqual('official_recorded_lap_duration', r['timingBasis'])
            self.assertTrue(r['sourceIds'])
            for speed,time in zip(r['lapSpeedsMph'],r['lapTimesS']):
                self.assertLess(abs(speed-9000/time),.001)

    def test_export_is_reproducible(self):
        for relative, text in artifacts().items():
            self.assertEqual((ROOT/'performance_explorer'/relative).read_bytes(),text.encode())

if __name__=='__main__': unittest.main()
