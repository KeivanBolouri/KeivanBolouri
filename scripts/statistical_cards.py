"""Deterministic educational figures in the reference Monte Carlo card style.

The models, seeds, and mathematical targets are those of the existing examples.
Rendering and animation timing are separate from the underlying calculations.
"""
from __future__ import annotations

from math import lgamma
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 880, 650
FRAME_MS, FRAMES_PER_EXPERIMENT = 250, 24
NAVY, INK, MUTED = '#14283d', '#e7eef8', '#bfccdd'
TEAL, PURPLE, BLUE = '#84e5d9', '#bbabec', '#7bbcf4'
ORANGE, RED, LINE = '#f4bb87', '#f5a0ad', '#334b64'
COLORS = [TEAL, PURPLE, BLUE, ORANGE, RED, '#c6d7ae']
EXPERIMENTS = [
    ('lasso-coefficients', 'How Lasso selects variables'),
    ('monte-carlo-card', 'Finding an integral with randomness'),
    ('missing-data-simulation', 'What changes when data go missing?'),
    ('bootstrap-sampling', 'How bootstrap sampling works'),
    ('confidence-intervals', 'What a confidence interval means'),
    ('federated-learning', 'How federated learning works'),
    ('gradient-descent', 'How optimization finds a minimum'),
    ('confounding-adjustment', 'Why adjust for a confounder?'),
    ('observation-intervention', 'Observing is not intervening'),
    ('bayesian-updating', 'From prior to posterior'),
    ('mcmc-sampling', 'Exploring a posterior with MCMC'),
]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'text.color': INK, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.edgecolor': LINE, 'axes.labelsize': 9})


def text(fig, x, y, value, pixels=15, color=INK, bold=False, serif=False, **kw):
    return fig.text(x / WIDTH, 1 - y / HEIGHT, value, fontsize=pixels * .72,
                    color=color, weight='bold' if bold else 'normal',
                    family='DejaVu Serif' if serif else 'DejaVu Sans',
                    va='top', **kw)


def card(index, frame, description, metadata, reference, metrics, note):
    fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100, facecolor=NAVY)
    text(fig, 30, 23, 'A STATISTICAL EXPERIMENT', 12, TEAL, True)
    text(fig, 30, 49, EXPERIMENTS[index][1], 27, bold=True, serif=True)
    for row, line in enumerate(description):
        text(fig, 30, 99 + 25 * row, line, 15)
    text(fig, 30, 163, metadata, 12, MUTED)
    text(fig, 850, 160, reference, 17, TEAL, True, True, ha='right')
    for i, (label, value, color) in enumerate(metrics):
        x = 30 + i * 278
        fig.add_artist(FancyBboxPatch((x / WIDTH, 1 - 568 / HEIGHT), 264 / WIDTH,
                       83 / HEIGHT, transform=fig.transFigure,
                       boxstyle='round,pad=0,rounding_size=.012',
                       facecolor='#192e44', edgecolor=LINE, linewidth=1))
        text(fig, x + 16, 499, label, 12, MUTED)
        text(fig, x + 16, 525, str(value), 25, color, True)
    text(fig, 30, 583, note, 12, MUTED)
    text(fig, 30, 613, 'Open the interactive experiment ↗', 14, TEAL, True)
    text(fig, 850, 616, f'{index + 1} / 11 · 6 seconds', 11, MUTED, ha='right')
    # A small timing indicator makes every frame distinct, including held states.
    fig.add_artist(Line2D([30 / WIDTH, (30 + 820 * (frame + 1) / FRAMES_PER_EXPERIMENT) / WIDTH],
                         [1 - 641 / HEIGHT] * 2, transform=fig.transFigure,
                         color=TEAL, alpha=.65, linewidth=1.5))
    return fig


def axes(fig, rect=(.09, .36, .865, .32), xlabel='', ylabel=''):
    # Reserve distinct lines for tick labels, axis titles, and the figure legend.
    x, y, width, height = rect
    rect = (x, y + .025, width, height - .025)
    ax = fig.add_axes(rect, facecolor=NAVY)
    ax.grid(color=LINE, linewidth=.7, alpha=.75)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.tick_params(labelsize=9, length=0, pad=7)
    ax.set_xlabel(xlabel, labelpad=6)
    ax.set_ylabel(ylabel, labelpad=6)
    return ax


def legend(fig, items, ncol=None):
    fig.legend(handles=[Line2D([0], [0], color=color, lw=2, ls=style, label=label)
                        for label, color, style in items], loc='center',
               bbox_to_anchor=(.52, 1 - 465 / HEIGHT), ncol=ncol or len(items),
               frameon=False, fontsize=8.4, labelcolor=MUTED,
               handlelength=2.1, columnspacing=1.8)


def finish(fig):
    fig.canvas.draw()
    bounds = fig.bbox
    renderer = fig.canvas.get_renderer()
    # Check the shared title, body, metrics, and footer for clipping.
    for label in fig.texts:
        box = label.get_window_extent(renderer)
        assert box.x0 >= 12 and box.x1 <= WIDTH - 12, (label.get_text(), box.bounds)
        assert box.y0 >= 0 and box.y1 <= HEIGHT, (label.get_text(), box.bounds)
    image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB')
    plt.close(fig)
    mask = Image.new('L', (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WIDTH - 1, HEIGHT - 1), radius=20, fill=255)
    result = Image.new('RGB', image.size, '#ffffff')
    result.paste(image, mask=mask)
    return result


def beta_pdf(x, a, b):
    out = np.zeros_like(x)
    keep = (x > 0) & (x < 1)
    out[keep] = np.exp(lgamma(a + b) - lgamma(a) - lgamma(b)
                       + (a - 1) * np.log(x[keep]) + (b - 1) * np.log1p(-x[keep]))
    return out


def prepare_data():
    d = {}
    z = np.array([2.4, -1.9, 1.35, -.95, .6, -.3])
    d['lasso'] = z
    rng = np.random.default_rng(2026)
    p = rng.uniform(0, 1, (1500, 2))
    d['mc'] = (p, p[:, 1] <= p[:, 0] ** 2)
    rng = np.random.default_rng(2026)
    x = rng.uniform(-2.5, 2.5, 120)
    y = .75 * x + rng.normal(0, 1.25, 120)
    d['missing'] = (x, y, np.argsort(y)[::-1], np.polyfit(x, y, 1))
    rng = np.random.default_rng(2718)
    observed = rng.normal(50, 11, 24)
    indices = rng.integers(0, 24, (640, 24))
    means = observed[indices].mean(axis=1)
    spread = np.max(abs(means - observed.mean()))
    bins = np.linspace(observed.mean() - spread - .5, observed.mean() + spread + .5, 24)
    d['bootstrap'] = (observed, indices, means, bins)
    assert np.isin(observed[indices], observed).all()
    rng = np.random.default_rng(20260912)
    means = rng.normal(0, 1, (80, 25)).mean(axis=1)
    margin = 1.959963984540054 / 5
    d['ci'] = (means, margin, abs(means) <= margin)
    angle = np.deg2rad(32)
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    matrix = rotation @ np.diag([3., .35]) @ rotation.T
    points = [np.array([-3., .4])]
    for _ in range(80):
        points.append(points[-1] - .13 * (matrix @ points[-1]))
    points = np.asarray(points)
    losses = np.einsum('ni,ij,nj->n', points, matrix, points) / 2
    assert np.all(np.diff(losses) < 0)
    d['optimization'] = matrix, points, losses
    rng = np.random.default_rng(20260912)
    z, u, e = rng.normal(size=(3, 4000))
    x, y = z + u, z + u + 1.8 * z + e
    sizes = np.unique(np.round(np.geomspace(40, 4000, 90)).astype(int))
    estimates = []
    for n in sizes:
        naive = np.linalg.lstsq(np.column_stack([np.ones(n), x[:n]]), y[:n], rcond=None)[0][1]
        adjusted = np.linalg.lstsq(np.column_stack([np.ones(n), x[:n], z[:n]]), y[:n], rcond=None)[0][1]
        zz = np.column_stack([np.ones(n), z[:n]])
        xr = x[:n] - zz @ np.linalg.lstsq(zz, x[:n], rcond=None)[0]
        yr = y[:n] - zz @ np.linalg.lstsq(zz, y[:n], rcond=None)[0]
        assert np.isclose(adjusted, xr @ yr / (xr @ xr))
        estimates.append((naive, adjusted))
    d['confounding'] = sizes, np.asarray(estimates)
    joint = {(z, x, y): .5 * ((.2 + .6 * z) if x else (1 - .2 - .6 * z))
             * ((.1 + .2 * x + .4 * z) if y else (1 - .1 - .2 * x - .4 * z))
             for z in (0, 1) for x in (0, 1) for y in (0, 1)}
    assert np.isclose(sum(joint.values()), 1)
    px1 = sum(p for (z, x, y), p in joint.items() if x == 1)
    obs_z = sum(p for (z, x, y), p in joint.items() if z == 1 and x == 1) / px1
    obs_y = sum(p for (z, x, y), p in joint.items() if y == 1 and x == 1) / px1
    do_y = sum(.5 * (.1 + .2 + .4 * z) for z in (0, 1))
    assert np.allclose([obs_z, obs_y, .5, do_y], [.8, .62, .5, .5])
    d['intervention'] = obs_z, obs_y, .5, do_y
    flips = np.random.default_rng(2026).binomial(1, .65, 80)
    heads = np.r_[0, np.cumsum(flips)]
    xx = np.linspace(0, 1, 2001)
    curves = np.array([beta_pdf(xx, 2 + h, 2 + n - h) for n, h in enumerate(heads)])
    expected = (2 + heads) / (4 + np.arange(81))
    assert np.max(abs(np.trapezoid(curves, xx, axis=1) - 1)) < 2e-6
    assert np.max(abs(np.trapezoid(curves * xx, xx, axis=1) - expected)) < 2e-6
    d['bayes'] = heads, xx, curves
    rng = np.random.default_rng(731)
    current, states, accepts = -2., [], []
    for _ in range(1120):
        before = current
        proposal = current + rng.normal(0, .9)
        take = np.log(rng.random()) < min(0, -((proposal - .5) ** 2 - (current - .5) ** 2))
        if take:
            current = proposal
        states.append(current)
        accepts.append(take)
        assert current == (proposal if take else before)
    samples = np.array(states)[200:]
    edges = np.arange(-2.2, 3.21, .3)
    assert samples.min() >= edges[0] and samples.max() <= edges[-1]
    d['mcmc'] = samples, edges
    return d


DATA = prepare_data()


def render(index, k):
    t = k / (FRAMES_PER_EXPERIMENT - 1)
    if index == 0:
        z = DATA['lasso']; penalty = 2.6 * t
        beta = np.sign(z) * np.maximum(abs(z) - penalty, 0)
        active = abs(beta) > 1e-12
        assert np.allclose((beta - z)[active] + penalty * np.sign(beta[active]), 0)
        assert np.all(abs((beta - z)[~active]) <= penalty + 1e-12)
        fig = card(index, k, ['Increase the penalty and watch coefficients shrink toward zero.',
                   'A coefficient at zero removes that predictor from the fitted model.'],
                   'Synthetic orthogonal predictors', 'Exact Lasso solutions',
                   [('Penalty (λ)', f'{penalty:.2f}', INK), ('Active variables', f'{active.sum()} / 6', TEAL),
                    ('Zero coefficients', f'{(~active).sum()} / 6', INK)],
                   'For an orthogonal design: β̂ = sign(z) × max(|z| − λ, 0).')
        ax = axes(fig, xlabel='Penalty (λ)', ylabel='Coefficient')
        grid = np.linspace(0, 2.6, 501)
        ax.set(xlim=(-.03, 2.65), ylim=(-2.25, 2.75))
        ax.set_xticks(np.arange(0, 2.6, .5)); ax.set_yticks([-2, -1, 0, 1, 2])
        ax.axhline(0, color=MUTED, lw=.8)
        shown = np.r_[grid[grid < penalty], penalty]
        for j, color in enumerate(COLORS):
            ax.plot(grid, np.sign(z[j]) * np.maximum(abs(z[j]) - grid, 0), color=color, alpha=.15)
            ax.plot(shown, np.sign(z[j]) * np.maximum(abs(z[j]) - shown, 0), color=color, lw=2)
            ax.plot(penalty, beta[j], 'o', color=color, ms=5)
        ax.axvline(penalty, color=MUTED, ls=':', lw=1)
        legend(fig, [(f'X{j+1}', c, '-') for j, c in enumerate(COLORS)])
    elif index == 1:
        points, hits = DATA['mc']; n = round(50 * 30 ** t)
        estimate = hits[:n].mean()
        fig = card(index, k, ['Scatter random points across a unit square. The fraction below the curve',
                   'estimates the area underneath it. Watch the estimate change as samples arrive.'],
                   'Uniform samples  ·  f(x) = x²', 'Exact integral = ⅓',
                   [('Samples drawn', f'{n:,}', INK), ('Estimated integral', f'{estimate:.4f}', TEAL),
                    ('Absolute error', f'{abs(estimate - 1/3):.4f}', INK)],
                   'Showing up to 900 points; estimates use every sample. Error can fluctuate.')
        ax = axes(fig); ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
        xx = np.linspace(0, 1, 200); ax.fill_between(xx, xx ** 2, color=TEAL, alpha=.09)
        shown = min(n, 900)
        ax.scatter(points[:shown, 0], points[:shown, 1], c=np.where(hits[:shown], '#68cfc5', '#9689be'), s=11, edgecolors='none')
        ax.plot(xx, xx ** 2, color=TEAL, lw=2)
        legend(fig, [('Below the curve', TEAL, '-'), ('Above the curve', PURPLE, '-')])
    elif index == 2:
        x, y, order, full = DATA['missing']
        removed = round(60 * (k / 11 if k < 12 else (23 - k) / 11))
        keep = np.ones(120, dtype=bool); keep[order[:removed]] = False
        fitted = np.polyfit(x[keep], y[keep], 1)
        fig = card(index, k, ['Keep one dataset fixed and selectively omit the largest outcomes.',
                   'The fitted association changes as observations disappear and return.'],
                   'Higher outcomes omitted first', 'Association, not causation',
                   [('Observations retained', f'{keep.sum()} / 120', INK), ('Fitted slope', f'{fitted[0]:.2f}', TEAL),
                    ('Full-data slope', f'{full[0]:.2f}', PURPLE)],
                   'Simulated data. Faint dots mark omitted observations; both lines describe association.')
        ax = axes(fig, xlabel='Predictor (X)', ylabel='Outcome (Y)')
        ax.set(xlim=(-2.75, 2.75), ylim=(-4.7, 4.7)); ax.set_yticks([-4, -2, 0, 2, 4])
        ax.scatter(x[~keep], y[~keep], color=MUTED, alpha=.15, s=15)
        ax.scatter(x[keep], y[keep], color=TEAL, alpha=.85, s=17)
        xx = np.array([-2.75, 2.75])
        ax.plot(xx, np.polyval(full, xx), color=PURPLE, ls='--', lw=1.8)
        ax.plot(xx, np.polyval(fitted, xx), color=TEAL, lw=2)
        legend(fig, [('Full-data fit', PURPLE, '--'), ('Retained-data fit', TEAL, '-')])
    elif index == 3:
        observed, indices, means, bins = DATA['bootstrap']; n = round(1 + 639 * t)
        hist, _ = np.histogram(means[:n], bins); assert hist.sum() == n
        fig = card(index, k, ['Resample the same observed values with replacement, then calculate a mean.',
                   'Repeat to build a bootstrap distribution of sample means.'],
                   'One fixed sample of 24 observations', 'Sampling with replacement',
                   [('Bootstrap resamples', f'{n:,}', INK), ('Original sample mean', f'{observed.mean():.2f}', PURPLE),
                    ('Latest resample mean', f'{means[n-1]:.2f}', TEAL)],
                   'Stacked dots show repeated draws. Every resample uses the same 24 observed values.')
        ax = axes(fig, (.09, .36, .38, .31), 'Observed value')
        ax.set(xlim=(observed.min()-3, observed.max()+3), ylim=(0, 1.65)); ax.set_yticks([])
        ax.text(.0, 1.03, 'Original sample and current resample', transform=ax.transAxes, color=MUTED, fontsize=8.5)
        ax.scatter(observed, np.full(24, 1.25), color=PURPLE, s=17)
        for j, amount in enumerate(np.bincount(indices[n-1], minlength=24)):
            ax.scatter(np.full(amount, observed[j]), .2 + .1 * np.arange(amount), s=17, color=TEAL)
        ax = axes(fig, (.59, .36, .365, .31), 'Bootstrap sample mean', 'Resamples')
        ax.bar(bins[:-1], hist, width=np.diff(bins)*.92, align='edge', color=TEAL, alpha=.65)
        ax.axvline(observed.mean(), color=PURPLE, ls='--', lw=1.8)
        ax.set(xlim=(bins[0], bins[-1]), ylim=(0, np.histogram(means,bins)[0].max()*1.15))
        legend(fig, [('Observed-sample mean', PURPLE, '--'), ('Bootstrap resamples', TEAL, '-')])
    elif index == 4:
        means, margin, covers = DATA['ci']; n = round(1 + 79 * t)
        fig = card(index, k, ['Repeated samples give different confidence intervals for one fixed mean.',
                   'Watch how often the intervals include the true population mean.'],
                   'Normal population · known SD = 1 · n = 25', 'True mean = 0',
                   [('Samples generated', f'{n} / 80', INK), ('Coverage so far', f'{covers[:n].mean():.1%}', TEAL),
                    ('Latest sample mean', f'{means[n-1]:+.2f}', INK)],
                   '95% is long-run coverage; the observed fraction varies between simulation runs.')
        ax = axes(fig, xlabel='Estimated mean and 95% confidence interval', ylabel='Sample number')
        ids = np.arange(n-1, max(-1,n-21), -1)
        for row, j in enumerate(ids):
            color = TEAL if covers[j] else RED
            ax.plot([means[j]-margin,means[j]+margin], [row,row], color=color, lw=1.7)
            ax.plot(means[j], row, 'o', color=color, ms=3)
        ax.axvline(0, color=PURPLE, ls='--', lw=1.5)
        lim = max(.8, abs(means).max()+margin+.05)
        ax.set(xlim=(-lim,lim), ylim=(19.8,-.8))
        ticks = [r for r in [0,4,9,14,19] if r < len(ids)]
        ax.set_yticks(ticks, [str(ids[r]+1) for r in ticks]); ax.grid(axis='y',visible=False)
        legend(fig, [('Contains true mean', TEAL, '-'), ('Misses true mean', RED, '-')])
    elif index == 5:
        phase = min(3, k//6); progress=(k%6)/5
        names=['Send model','Fit locally','Share updates','Aggregate']
        fig = card(index, k, ['Three sites learn from local observations and share model updates.',
                   'A coordinator combines their updates into a shared model.'],
                   'Model parameters travel; observations stay local', names[phase],
                   [('Participating sites','3',INK),('Communication phase',f'{phase+1} / 4',TEAL),
                    ('Aggregation','Weighted',INK)], 'Conceptual illustration. Aggregation weights reflect each site’s sample size.')
        ax=fig.add_axes([.06,.32,.88,.38],facecolor=NAVY);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        for j,y in enumerate([.82,.5,.18]):
            start,end=(np.array([.72,.5]),np.array([.28,y])) if phase==0 else (np.array([.28,y]),np.array([.72,.5]))
            col=TEAL if phase in (0,2) else LINE
            ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=12,color=col,lw=1.5))
            if phase in (0,2):
                point=start+(end-start)*progress;ax.plot(*point,'o',ms=7,color=TEAL)
            ax.add_patch(FancyBboxPatch((.01,y-.11),.27,.22,boxstyle='round,pad=.007',facecolor='#192e44',edgecolor=TEAL if phase==1 else LINE,lw=1.3))
            ax.text(.035,y+.035,f'Site {j+1}',color=INK,weight='bold',fontsize=11)
            ax.text(.035,y-.055,'Local observations',color=MUTED,fontsize=9)
            if phase==1:ax.plot([.035,.035+.21*progress],[y-.087]*2,color=TEAL,lw=2)
        ax.add_patch(FancyBboxPatch((.73,.33),.25,.34,boxstyle='round,pad=.007',facecolor='#192e44',edgecolor=PURPLE if phase==3 else LINE,lw=1.5))
        ax.text(.855,.535,'Coordinator',ha='center',color=INK,weight='bold',fontsize=12)
        ax.text(.855,.425,'Shared model',ha='center',color=MUTED,fontsize=10)
    elif index == 6:
        matrix, points, losses=DATA['optimization']; n=round(80*t)
        fig=card(index,k,['Follow actual gradient-descent steps across a curved loss surface.',
                 'The learning rate controls the size of each downhill step.'],
                 'Positive-definite quadratic loss','Minimum at (0, 0)',
                 [('Iteration',f'{n} / 80',INK),('Loss',f'{losses[n]:.4f}',TEAL),('Learning rate','0.13',INK)],
                 'Every position is an actual iterate. Contours connect points with equal loss.')
        ax=axes(fig,(.09,.36,.47,.32),'Parameter 1','Parameter 2')
        xx,yy=np.meshgrid(np.linspace(-3.3,3.3,150),np.linspace(-2.7,2.7,150))
        zz=(matrix[0,0]*xx**2+2*matrix[0,1]*xx*yy+matrix[1,1]*yy**2)/2
        ax.contour(xx,yy,zz,levels=[.025,.12,.4,.9,1.8,3.3,5.5,8.5,13,20],colors=LINE,linewidths=.8)
        ax.plot(points[:n+1,0],points[:n+1,1],color=TEAL,lw=2)
        ax.plot(*points[n],'o',color=TEAL,ms=7);ax.plot(0,0,'*',color=PURPLE,ms=12)
        ax.set(xlim=(-3.3,3.3),ylim=(-2.7,2.7));ax.set_xticks([-3,0,3])
        ax=axes(fig,(.7,.36,.255,.32),'Iteration','Loss (log scale)')
        ax.set(xlim=(0,80),ylim=(losses[-1]/1.5,losses[0]*1.5),yscale='log')
        ax.plot(np.arange(n+1),losses[:n+1],color=TEAL,lw=2);ax.set_xticks([0,40,80])
        legend(fig,[('Gradient descent',TEAL,'-'),('Minimum',PURPLE,'-')])
    elif index == 7:
        sizes,estimates=DATA['confounding']; j=round(89*t);n=sizes[j]
        fig=card(index,k,['A shared cause can distort the association estimated from observational data.',
                 'Adjusting for the measured confounder targets the causal effect in this model.'],
                 'X = Z + u; Y = X + 1.8Z + e','True effect = 1.00',
                 [('Observations',f'{n:,}',INK),('Unadjusted slope',f'{estimates[j,0]:.2f}',ORANGE),
                  ('Adjusted for Z',f'{estimates[j,1]:.2f}',TEAL)],
                 'Z, u, e are independent standard normals. Z is observed and the linear model is correct.')
        ax=axes(fig,xlabel='Number of observations',ylabel='Estimated effect of X on Y')
        ax.set_xscale('log');ax.set_xlim(35,4500)
        ax.set_ylim(min(.9,estimates.min()-.1),max(2,estimates.max()+.1))
        ax.set_xticks([40,100,400,1000,4000],['40','100','400','1,000','4,000'])
        ax.axhline(1,color=PURPLE,ls='--',lw=1.5);ax.axhline(1.9,color=ORANGE,ls=':',alpha=.6)
        ax.plot(sizes[:j+1],estimates[:j+1,0],color=ORANGE,lw=2)
        ax.plot(sizes[:j+1],estimates[:j+1,1],color=TEAL,lw=2)
        ax.scatter([n,n],estimates[j],color=[ORANGE,TEAL],s=24)
        legend(fig,[('Unadjusted',ORANGE,'-'),('Adjusted for Z',TEAL,'-'),('True effect',PURPLE,'--')])
    elif index == 8:
        phase=0 if k<8 else 1 if k<16 else 2
        obs_z,obs_y,do_z,do_y=DATA['intervention']
        mode=['Observe X = 1','Changing the model','Set X = 1'][phase]
        zz,yy=(obs_z,obs_y) if phase==0 else (do_z,do_y)
        suffix=' | X = 1)' if phase==0 else ' | do(X = 1))'
        metrics=[('Operation',['Observe','Switching','Intervene'][phase],INK),
                 ('P(Z = 1'+suffix,'—' if phase==1 else f'{zz:.2f}',PURPLE),
                 ('P(Y = 1'+suffix,'—' if phase==1 else f'{yy:.2f}',TEAL)]
        fig=card(index,k,['Observing X = 1 selects cases where X is already 1.',
                 'Intervening sets X to 1 and removes only the incoming arrow from Z.'],
                 'Z is a common cause of X and Y',mode,metrics,
                 'P(Z=1)=0.5; P(X=1|Z)=0.2+0.6Z; P(Y=1|X,Z)=0.1+0.2X+0.4Z.')
        ax=fig.add_axes([.13,.325,.74,.39],facecolor=NAVY);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        nodes={'Z':(.5,.82),'X':(.19,.2),'Y':(.81,.2)}
        for a,b,col in [('Z','X',PURPLE),('Z','Y',MUTED),('X','Y',TEAL)]:
            if a=='Z' and b=='X' and phase==2:continue
            alpha=1-(k-8)/7 if a=='Z' and b=='X' and phase==1 else 1
            ax.annotate('',xy=nodes[b],xytext=nodes[a],arrowprops={'arrowstyle':'-|>','shrinkA':25,'shrinkB':27,'color':col,'lw':2,'alpha':alpha,'mutation_scale':16})
        for name,(x,y) in nodes.items():
            col=PURPLE if name=='Z' else TEAL
            ax.text(x,y,'X = 1' if name=='X' else name,ha='center',va='center',color=col,weight='bold',fontsize=15,
                    bbox={'boxstyle':'round,pad=.5','facecolor':'#192e44','edgecolor':col})
        if phase==2:ax.text(.21,.62,'Incoming arrow removed',ha='center',color=TEAL,fontsize=9)
        ax.text(.5,.995,'Common cause',ha='center',color=MUTED,fontsize=9)
    elif index == 9:
        heads,xx,curves=DATA['bayes'];n=round(80*t);h=heads[n];post=(2+h)/(4+n)
        fig=card(index,k,['Begin with a prior distribution for the probability of heads.',
                 'As simulated coin flips arrive, update it to the posterior distribution.'],
                 'Beta(2, 2) prior · simulated coin flips','Exact Bayesian update',
                 [('Coin flips observed',f'{n} / 80',INK),('Heads / tails',f'{h} / {n-h}',INK),
                  ('Posterior mean',f'{post:.3f}',TEAL)],
                 'Posterior = Beta(2 + heads, 2 + tails). Prior and data together determine the curve.')
        ax=axes(fig,xlabel='Probability of heads',ylabel='Probability density')
        ax.set(xlim=(0,1),ylim=(0,np.ceil(curves.max()*1.12)))
        ax.fill_between(xx,curves[n],color=TEAL,alpha=.12)
        ax.plot(xx,curves[0],color=PURPLE,lw=1.8,ls='--');ax.plot(xx,curves[n],color=TEAL,lw=2)
        legend(fig,[('Prior',PURPLE,'--'),('Posterior',TEAL,'-')])
    else:
        samples,edges=DATA['mcmc'];n=round(30+890*t)
        hist,_=np.histogram(samples[:n],edges);width=np.diff(edges)
        assert hist.sum()==n and np.isclose(np.sum(hist/(n*width)*width),1)
        fig=card(index,k,['A random-walk Metropolis chain explores a posterior distribution.',
                 'Retained states build a histogram; rejected proposals repeat the current state.'],
                 'Normal prior + one observation · 200 warmup steps','Posterior mean = 0.50',
                 [('Retained samples',f'{n:,}',INK),('Sample mean',f'{samples[:n].mean():.2f}',TEAL),
                  ('Current state',f'{samples[n-1]:.2f}',INK)],
                 'Correlated samples. Repeated states count; a finite run does not prove convergence.')
        ax=axes(fig,xlabel='Parameter value (θ)',ylabel='Density')
        xx=np.linspace(edges[0],edges[-1],650);pdf=np.exp(-(xx-.5)**2)/np.sqrt(np.pi)
        counts=[round(30+890*j/23) for j in range(24)]
        ymax=max(np.max(np.histogram(samples[:m],edges)[0]/(m*width)) for m in counts)*1.16
        ax.set(xlim=(edges[0],edges[-1]),ylim=(0,max(.9,ymax)))
        ax.bar(edges[:-1],hist/(n*width),width=width*.94,align='edge',color=TEAL,alpha=.45)
        ax.plot(xx,pdf,color=PURPLE,ls='--',lw=2)
        current=samples[n-1];yy=np.exp(-(current-.5)**2)/np.sqrt(np.pi)
        ax.plot([current,current],[0,yy],color=TEAL,ls=':',lw=1)
        ax.plot(current,yy,'o',color=TEAL,ms=6)
        legend(fig,[('Exact posterior',PURPLE,'--'),('Retained samples',TEAL,'-')])
    return finish(fig)
