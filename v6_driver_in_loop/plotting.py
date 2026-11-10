"""Optional standalone scientific figures (matplotlib); no model/UI coupling."""
import math
from .track import OvalTrack


def plot_result(result, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    samples=result.samples
    t=[s.sim_time_s for s in samples]
    cfg=result.metadata['track']
    track=OvalTrack(cfg['straight_length_m'],cfg['radius_m'],cfg['width_m'])
    reference=[track.point(i*track.length_m/800) for i in range(801)]
    fig,axes=plt.subplots(3,2,figsize=(12,10))
    ax=axes[0,0]
    ax.plot([p.x_m for p in reference],[p.y_m for p in reference],'--',color='gray',label='Reference')
    ax.plot([s.x_m for s in samples],[s.y_m for s in samples],label='SIMULATED driven path')
    for offset in (-track.width_m/2,track.width_m/2):
        ax.plot([p.x_m-offset*math.sin(p.heading_rad) for p in reference],
                [p.y_m+offset*math.cos(p.heading_rad) for p in reference],lw=.5,color='gray')
    ax.set(xlabel='World x (m)',ylabel='World y (m)',title='Approximate stadium oval');ax.set_aspect('equal');ax.legend(fontsize=8)
    axes[0,1].plot(t,[s.speed_m_s for s in samples],label='Actual speed')
    axes[0,1].plot(t,[s.target_speed_m_s for s in samples],'--',label='Current driver target')
    axes[0,1].set(ylabel='Speed (m/s)');axes[0,1].legend(fontsize=8)
    axes[1,0].step(t,[s.steering_command_rad for s in samples],where='post');axes[1,0].set(ylabel='Steering (rad)')
    axes[1,1].step(t,[s.throttle_command for s in samples],where='post',label='Throttle')
    axes[1,1].step(t,[s.brake_command for s in samples],where='post',label='Brake');axes[1,1].set(ylabel='Applied pedal (0–1)');axes[1,1].legend(fontsize=8)
    axes[2,0].plot(t,[s.lateral_accel_m_s2 for s in samples]);axes[2,0].set(ylabel='Lateral body acceleration (m/s²)')
    axes[2,1].plot(t,[s.path_error_m for s in samples]);axes[2,1].axhline(track.width_m/2,color='red',ls='--');axes[2,1].axhline(-track.width_m/2,color='red',ls='--');axes[2,1].set(ylabel='Tracking error (m)')
    for ax in axes.flat:
        ax.grid(alpha=.2)
        if ax is not axes[0,0]:ax.set_xlabel('Simulated time (s)')
    fig.suptitle(f'SIMULATED V6 engineering telemetry — {result.status}; {result.elapsed_sim_s:.3f} s')
    fig.tight_layout();fig.savefig(path,dpi=150);plt.close(fig)
