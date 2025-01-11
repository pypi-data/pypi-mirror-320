from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import ehtim as eh
from scipy.ndimage import gaussian_filter
from   ehtim.calibrating import self_cal as sc

# change to 'direct' if you don't have nfft installed
ttype='nfft'

path = eh.__path__[0]

# Load the image and the array
im = eh.image.load_image(path+'/../models/avery_sgra_eofn.txt')
eht = eh.array.load_txt(path+'/../arrays/EHT2017.txt')

# Add an artifical spectral index to the image
alpha1 = -2.5
alpha2 = 1

specarr = np.zeros(im.imvec.shape).reshape((im.ydim,im.xdim))
mask = im.imarr() > .5*np.max(im.imvec)
specarr[~mask] = alpha1
specarr[mask] = alpha2
specarr = gaussian_filter(specarr, (4, 4))
im.specvec = specarr.flatten()
im230 = im.get_image_mf(230.e9)
im345 = im.get_image_mf(345.e9)

# Observe the image at two different frequencies
tint_sec = 60
tadv_sec = 600
tstart_hr = 0
tstop_hr = 24
bw_hz = 2e9
obs230 = im230.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz,
                     sgrscat=False, ampcal=True, phasecal=True)
obs345 = im345.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz,
                        sgrscat=False, ampcal=True, phasecal=True)
obslist = [obs230,obs345]

# Resolution
beamparams230 = obs230.fit_beam() # fitted beam parameters (fwhm_maj, fwhm_min, theta) in radians
res230 = obs230.res() # nominal array resolution, 1/longest baseline
beamparams345 = obs345.fit_beam() # fitted beam parameters (fwhm_maj, fwhm_min, theta) in radians
res345 = obs345.res() # nominal array resolution, 1/longest baseline
print("Nominal Resolution 230 GHz: %.1f uas"%(res230/eh.RADPERUAS))
print("Nominal Resolution 345 GHz: %.1f uas"%(res345/eh.RADPERUAS))

# Determine zero-baseline spectral index
zbllist = np.array([im230.total_flux(),im345.total_flux()])
rflist = np.array([im230.rf,im345.rf])
alpha0 = np.polyfit(np.log(rflist), np.log(zbllist), 1)[0]

# Generate an image prior
npix = 64
fov = 1*im.fovx()
zbl = im.total_flux() # total flux
prior_fwhm = 200*eh.RADPERUAS # Gaussian size in microarcssec
emptyprior = eh.image.make_square(obs230, npix, fov)
flatprior = emptyprior.add_flat(zbl)
gaussprior = emptyprior.add_gauss(zbl, (prior_fwhm, prior_fwhm, 0, 0, 0))

# Image both frequencies together with spectral index using complex visibilities
plt.close('all')
#gaussprior = gaussprior.add_const_mf(alpha0) # add an initial constant spectral index
gaussprior = gaussprior.add_const_mf(0,0) # add an initial constant spectral index

imgr  = eh.imager.Imager(obslist, gaussprior, gaussprior, zbl,
                          data_term={'vis':1},
                          reg_term={'tv':0.1,'l1':0.1,'tv_alpha':0.5,'l2_alpha':0.001},
                          #reg_term={'tv':0.05,'l1':0.1,'tv_alpha':0.5},                          
                          norm_reg=True,
                          epsilon_tv = 1.e-10,
                          mf=True, mf_order=1,
                          maxit=100, ttype=ttype)
imgr.make_image_I(mf=True,show_updates=False)
out = imgr.out_last()

for i in range(5): # blur and reimage
    out = out.blur_circ(res230)
    imgr.maxit_next=1000
    imgr.init_next = out
    imgr.make_image_I(mf=True,show_updates=False)
    out = imgr.out_last()
    
# look at results
out230_mf = out.get_image_mf(230.e9)
out345_mf = out.get_image_mf(345.e9)

out230_mf.display()
out345_mf.display()
out.display(pol='spec');
out.display(pol='curv');


