from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import ehtim as eh
import time
import os

plt.close('all')
path = eh.__path__[0]

# Fourier transform type - change this to 'direct' if 'nfft' is not installed!!!
ttype = 'nfft'

# Load the image and the telescope array
im = eh.image.load_image(path+'/../models/rowan_m87.txt')
eht = eh.array.load_txt(path+'/../arrays/EHT2017.txt')

# Regrid the image for display
imdisp = im.regrid_image(120*eh.RADPERUAS, 512)

# Look at the image
imdisp.display();
imdisp.blur_circ(15*eh.RADPERUAS).display();

# simulate and save an EHT observation
# ampcal and phasecal determine if gain variations and phase errors are included
# for now, let's assume we can calibrate both amplitude and phase
# try changing phasecal=False and see what happens!

# simulation parameters
tint_sec = 60  # Integration time in seconds, 
tadv_sec = 600 # Advance time between scans
tstart_hr = 0  # GMST time of the start of the observation
tstop_hr = 24  # GMST time of the end of the observation
bw_hz = 4.e9   # Bandwidth in Hz

# generate the observation
obs = im.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz,
                 sgrscat=False, ampcal=True, phasecal=True)

# Image Parameters
npix = 100
fov = 120*eh.RADPERUAS
zbl = im.total_flux() # total flux
print(zbl)

# What is the resolution of the observation? 
beamparams = obs.fit_beam() # fitted beam parameters (fwhm_maj, fwhm_min, theta) in radians
res = obs.res()             # nominal array resolution, 1/longest baseline


print("Clean beam parameters: [%.1f uas,%.1f uas,%.1f deg]"
      %(beamparams[0]/eh.RADPERUAS, beamparams[1]/eh.RADPERUAS,beamparams[2]/eh.DEGREE))
print("Nominal Resolution: %.1f uas"%(res/eh.RADPERUAS))

# Set up an image prior
prior_fwhm = 50*eh.RADPERUAS # Gaussian size in microarcssec
emptyprior = eh.image.make_square(obs, npix, fov)
flatprior = emptyprior.add_flat(zbl)
gaussprior = emptyprior.add_gauss(zbl, (prior_fwhm, prior_fwhm, 0, 0, 0))

#################################################################
# Image total flux with visibilities
data_term={'vis':1}              # data term weights
reg_term = {'tv2':1, 'l1':0.1}   # regularizer term weights


# set up the imager (visibilities)
imgr  = eh.imager.Imager(obs, gaussprior, prior_im=gaussprior, flux=zbl,
                         data_term=data_term, reg_term=reg_term, 
                         norm_reg=True, # this is very important!
                         epsilon_tv = 1.e-10,
                         maxit=250, ttype=ttype)
                         

# run the imager 
imgr.make_image_I(show_updates=False,niter=5)
imgr.init_next = imgr.out_last().blur_circ(res)
imgr.maxit_next = 500
imgr.make_image_I(show_updates=False,niter=5)
out = imgr.out_last()
outblur = out.blur_circ(res)
out.display();
outblur.display();

#################################################################
# set up the imager (amplitudes and closure phase)
#data_term={'logcamp':1,'cphase':0.5} # data term weights
data_term={'amp':1,'cphase':0.5} # data term weights

#reg_term = {'tv2':1, 'l1':0.1}   # regularizer term weights
reg_term = {'tv2':1, 'l1':0.1}   # regularizer term weights

# set up the imager
imgr  = eh.imager.Imager(obs, gaussprior, prior_im=gaussprior, flux=zbl,
                         data_term=data_term, reg_term=reg_term, 
                         norm_reg=True, # this is very important!
                         epsilon_tv = 1.e-10,
                         maxit=250, ttype=ttype)

# run the imager
imgr.make_image_I(show_updates=False, niter=5)
imgr.init_next = imgr.out_last().blur_circ(res)
imgr.maxit_next = 500
imgr.make_image_I(show_updates=False,niter=5)
out = imgr.out_last()
outblur = out.blur_circ(res)
out.display();
outblur.display();


#################################################################
# set up the imager (log closure amplitudes and closure phase)
data_term={'logcamp':1,'cphase':0.5} # data term weights
reg_term = {'tv2':1, 'l1':0.1}   # regularizer term weights

# set up the imager
imgr.init_next = gaussprior
imgr.dat_term_next = data_term
imgr.reg_term_next = reg_term
imgr.maxit_next = 250

# image the first time
imgr.make_image_I(show_updates=False, niter=5)
imgr.init_next = imgr.out_last().blur_circ(res)
imgr.maxit_next = 500
imgr.make_image_I(show_updates=False,niter=5)
out = imgr.out_last()
outblur = out.blur_circ(res)
out.display();
outblur.display();



