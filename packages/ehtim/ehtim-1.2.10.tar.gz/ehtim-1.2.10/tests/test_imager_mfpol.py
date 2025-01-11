from __future__ import division
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import ehtim as eh
from scipy.ndimage import gaussian_filter
from   ehtim.calibrating import self_cal as sc

# change to 'direct' if you don't have nfft installed
ttype='nfft'

path = '.'# eh.__path__[0]
obs = eh.obsdata.load_uvfits(path+'/../data/hops_lo_3601_M87+zbl-dtcal_selfcal.uvfits')
eht = eh.array.load_txt(path+'/../arrays/EHT2025.txt')
plt.ion()

    
# Define the parameters
alpha1 = -1.5  #-2.5
alpha2 = 1
beta1 = 0
beta2 = 0
malpha1 = 1.1
malpha2 = -2.4
rm1 = 2
rm2 = -1

maskfrac = 0.1

npix = 256
fov = 300 * eh.RADPERUAS

emptyprior = eh.image.make_square(obs, npix, fov)

# Create Gaussian blobs
im2 = emptyprior.add_gauss(1, (30 * eh.RADPERUAS, 30 * eh.RADPERUAS, 45 * eh.DEGREE, 0, 0))
mask2 = im2.imvec > maskfrac * np.max(im2.imvec)
im2.specvec = np.zeros(im2.imvec.shape)
im2.specvec[mask2] = alpha2
im2.curvvec = np.zeros(im2.imvec.shape)
im2.curvvec[mask2] = beta2

im1 = emptyprior.add_gauss(1, [30 * eh.RADPERUAS, 30 * eh.RADPERUAS, 0, 50 * eh.RADPERUAS, 50 * eh.RADPERUAS])
mask1 = im1.imvec > maskfrac * np.max(im1.imvec)
im1.specvec = np.zeros(im1.imvec.shape)
im1.specvec[mask1] = alpha1
im1.curvvec = np.zeros(im1.imvec.shape)
im1.curvvec[mask1] = beta1

# Combine the images
im = emptyprior.copy()
im.specvec = np.zeros(im.imvec.shape)
im.curvvec = np.zeros(im.imvec.shape)
im.imvec += im1.imvec
im.specvec += im1.specvec
im.curvvec += im1.curvvec
im.imvec += im2.imvec
im.specvec += im2.specvec
im.curvvec += im2.curvvec

# Initialize qvec and uvec for polarization calculations with some initial values
im1.qvec = np.zeros(im1.imvec.shape)
im1.uvec = np.zeros(im1.imvec.shape)
im1.qvec[mask1] = 0.1*im.imvec[mask1]
im1.uvec[mask1] = -0.1*im.imvec[mask1]

im2.qvec = np.zeros(im2.imvec.shape)
im2.uvec = np.zeros(im2.imvec.shape)
im2.qvec[mask2] = 0.1*im.imvec[mask2]
im2.uvec[mask2] = 0.25*im.imvec[mask2] 

im.qvec = np.zeros(im.imvec.shape)
im.uvec = np.zeros(im.imvec.shape)
im.vvec = np.zeros(im.imvec.shape)
im.qvec += im1.qvec
im.qvec += im2.qvec
im.uvec += im1.uvec
im.uvec += im2.uvec

# Adding a floor to the I, Q, and U values
I_floor = 1e-20

mask = im.imvec<I_floor
im.imvec[mask] = I_floor
im.qvec[im.qvec<=0] = im.imvec[im.qvec<=0]*1.e-6

# Set polarization spectral index
im2.specvec_pol = np.zeros(im2.imvec.shape)
im2.curvvec_pol = np.zeros(im2.imvec.shape)
im2.specvec_pol[mask2] = malpha2
im2.curvvec_pol[mask2] = 0

im1.specvec_pol = np.zeros(im1.imvec.shape)
im1.curvvec_pol= np.zeros(im1.imvec.shape)
im1.specvec_pol[mask1] = malpha1
im1.curvvec_pol[mask1] = 0

im.specvec_pol = np.zeros(im.imvec.shape)
im.curvvec_pol = np.zeros(im.imvec.shape)
im.specvec_pol += im1.specvec_pol
im.specvec_pol += im2.specvec_pol
im.curvvec_pol += im1.curvvec_pol
im.curvvec_pol += im2.curvvec_pol

# Assign RM vector
im1.rmvec = np.zeros(im1.imvec.shape)
im2.rmvec = np.zeros(im2.imvec.shape)
im1.rmvec[mask1] = rm1
im2.rmvec[mask2] = rm2

im.rmvec = np.zeros(im.imvec.shape)
im.rmvec += im1.rmvec
im.rmvec += im2.rmvec

# Display the combined image
#im.display()
im.display(pol='spec')

# Get images at different frequencies
im230 = im.get_image_mf(230e9)
im345 = im.get_image_mf(345e9)

# Display the images
#im230.display(plotp=True)
#im345.display(plotp=True)
print(im.total_flux(), im230.total_flux(), im345.total_flux())
print(im.evpa()/eh.DEGREE, im230.evpa()/eh.DEGREE, im345.evpa()/eh.DEGREE)
print(im.lin_polfrac(), im230.lin_polfrac(), im345.lin_polfrac())

# Display Stokes Q and U
#delta_chi = im345.chivec - im230.chivec
#plt.figure()
#plt.imshow(delta_chi.reshape((im345.xdim, im345.ydim)), cmap='Spectral',vmin=-0.5*np.pi,vmax=0.5*np.pi)
#plt.title('Delta Chi')
#plt.colorbar()
#plt.show()

plt.figure()
plt.imshow(im.rmvec.reshape((im.xdim, im.ydim)), cmap='Spectral',vmin=-3,vmax=3)
plt.title('RM')
plt.colorbar()
plt.show()

########################################################################################
# Generate Observations 
########################################################################################
tint_sec = 60
tadv_sec = 600
tstart_hr = 0
tstop_hr = 24
bw_hz = 4e9
obs230 = im230.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz,
                     sgrscat=False, ampcal=True, phasecal=True)
obs345 = im345.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz,
                        sgrscat=False, ampcal=True, phasecal=True)



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

########################################################################################
#  image total intensity and then polarization
########################################################################################

# Generate an image prior
npix = 64
fov = im.fovx()
zbl = im230.total_flux() # total flux
prior_fwhm = 200*eh.RADPERUAS # Gaussian size in microarcssec
emptyprior = eh.image.make_square(obs230, npix, fov)
flatprior = emptyprior.add_flat(zbl)
gaussprior = emptyprior.add_gauss(zbl, (prior_fwhm, prior_fwhm, 0, 0, 0))

# Image both frequencies together with spectral index using complex visibilities
plt.close('all')
prior = gaussprior.copy()
prior = prior.add_const_mf(0,0) # add an initial constant spectral index
obslist = [obs230,obs345]

imgr  = eh.imager.Imager(obslist, prior, prior, zbl,
                          data_term={'vis':1},
                          reg_term={'tv':5,'l1':0.1,'tv_alpha':1,'l2_alpha':1},
                          norm_reg=True,
                          epsilon_tv = 1.e-10,
                          mf=True, mf_order=1,
                          maxit=100, ttype=ttype)
imgr.transform_next = np.array(['log'])
imgr.make_image_I(mf=True,show_updates=False)
out = imgr.out_last()
for i in range(5): # blur and reimage
    outblur = out.blur_mf(rflist, res230)
    imgr.maxit_next=1000
    imgr.init_next = outblur
    imgr.make_image_I(mf=True,show_updates=False)
    out = imgr.out_last()
out230_mf = out.get_image_mf(230.e9)
out345_mf = out.get_image_mf(345.e9)

out230_mf.display()
out345_mf.display()
out.display(pol='spec',cbar_lims=[-3,3]);  
outblur = out.blur_mf(rflist,res230)

# Image both frequencies together in polarization
imgr  = eh.imager.Imager(obslist, out, out, zbl,
                          data_term={'pvis':1}, pol='P',
                          reg_term={'hw':0.1,'tv_alphap':1,'tv_rm':1},
                          norm_reg=True,
                          epsilon_tv = 1.e-6,
                          mf=True, mf_order=0,mf_order_pol=1,mf_rm=True,
                          maxit=100, ttype=ttype)
imgr.transform_next = np.array(['mcv'])
imgr.make_image_P(mf=True,show_updates=False)
out = imgr.out_last()
for i in range(2): # blur and reimage
    outblur = out.blur_mf(rflist, 0.5*res230) # TODO blur only polarization!!
    imgr.maxit_next=500
    imgr.init_next = outblur
    imgr.make_image_P(mf=True,show_updates=False)
    out = imgr.out_last()
out = imgr.out_last()

# make plot #############################################################
outblur = out.blur_mf(rflist, 0.25*res230)

rmscale = 0.5*(out.rf/eh.C)**2
inrm = im.rmvec.reshape((im.xdim, im.ydim))*rmscale
outrm = outblur.rmvec.reshape((out.xdim, out.ydim))*rmscale
inimarr = im.imvec.reshape((im.xdim,im.ydim))
outimarr = outblur.imvec.reshape((out.xdim,out.ydim))
plt.close('all')

fig, ax = plt.subplots()
clevels = np.max(im.imvec)*np.flip(np.array([1,0.5,0.25,0.125]))
cax=ax.imshow(inrm, cmap='Spectral',vmin=-3*rmscale,vmax=3*rmscale,interpolation='gaussian')
ax.contour(inimarr, colors='black', levels=clevels, colorbar=False, linewidths=0.5)
cbar = fig.colorbar(cax, ax=ax, label=r'RM (rad/m$^2$)')
plt.axis('off')
plt.show()

fig, ax = plt.subplots()
clevels = np.max(outimarr)*np.flip(np.array([1,0.5,0.25,0.125]))
outrm[outimarr< clevels[0]*.5] = np.nan
cax=ax.imshow(outrm, cmap='Spectral',vmin=-3*rmscale,vmax=3*rmscale,interpolation='gaussian')
ax.contour(outimarr, colors='black', levels=clevels, colorbar=False, linewidths=0.5)
cbar = fig.colorbar(cax, ax=ax, label=r'RM (rad/m$^2$)')
plt.axis('off')
plt.show()

# Get images at different frequencies
out230 = outblur.get_image_mf(230e9)
out345 = outblur.get_image_mf(345e9)

out230.display(plotp=True,pcut=0.1,label_type='scale',cbar_unit=['Tb'],has_title=False)
out345.display(plotp=True,pcut=0.1,label_type='scale',cbar_unit=['Tb'],has_title=False)
