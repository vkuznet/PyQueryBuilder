PyQB Queries
============
Here we provide examples of PyQB Queries used on CMS DBS.

.. doctest::

   find dataset where dataset=*Cosmics*
   find dataset where run=148126
   find block   where dataset=/Wgamma/Winter09_IDEAL_V12_FastSim_v1/GEN-SIM-DIGI-RECO
   find file.numevents where file.createdate = 2011-10-10 or run = 148126
   find count(file), sum(file.size) where block=/ExpressPhysics/Commissioning10-Express-v6/FEVT#f86bef6a-86c2-48bc-9f46-2e868c13d86e


