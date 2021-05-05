.. _rfactor:


Rainfall erosivity
==================

Introduction
------------

The soil erosive power of rainfall is quantified in the rainfall erosivity factor
:math:`R`. This is a measure for the total erosivity of a number of rainfall
events within a defined timeframe (years, months, number of days). The factor
is computed by first calculating the erosivity for every rainfall event
:math:`k` in a timeseries. Secondly, the sum of the erosivity of all events
is computed, for every year. Finally, the mean is computed over all the years:

.. math::

    R = \frac{1}{n}\sum_{j=1}^{n}[\sum_{k=1}^{m_j}E_k.(I_{30})_k]_j

with
 - :math:`R`: rainfall erosivity factor(:math:`\frac{\text{J
   .mm}}{\text{m}^2.\text{h.year}}`),
 - :math:`n`, increment :math:`j`: number of years,
 - :math:`m_j`, increment :math:`k`: number of rain event in year :math:`j`,
 - :math:`E`: the total kinetic energy of one single rain event
   (:math:`\frac{J}{m^2}`), and
 - :math:`I_{30}` (:math:`\frac{mm}{h}`): the maximum rain intensity
   recorded within 30 consecutive minutes.

In the above equation, the erosivity of one event is defined by the sum of the
depth of rainfall (mm) multiplied by the total kinetic energy of the event.
The latter is defined as:

.. math::

    E = \sum_{r=1}^o e_r \Delta V_r

with
 - :math:`o`: the number of increments for a particular rain event,
 - :math:`e_r`: the rain energy per unit depth,
   (:math:`\frac{\text{J}}{\text{m}^{2}.\text{mm}}`), and
 - :math:`\Delta V_r`: the rain depth (mm).

Energy per unit depth of rain
-----------------------------

There are number of ways to compute the rain energy per unit depth
:math:`e_r`, depending on the area for which the R-factor is computed. For an
application for Flanders/Belgium, the rain energy per unit is defined by
(Salles et al., 1999, 2002, Verstraeten et al., 2006):

.. math::

    e_r = 11.12i_r^{0.31}

with

 - :math:`i_r`: the rain intensity for every 10-min increment
   (mm :math:`\text{h}^{-1}`).

Prior to the relation estimated for Belgium, an alternative relation was
estimated for the USA by Brown and Foster (1987) (see also RUSLE-handbook,
Renard et al., 1997):

.. math::

    e_r = 29(1-0.72e^{-0.05i_r})

The use of the type of relation has an important implication on the
computation of the R-factor, as the sensitivity of the R-factor for extreme
high-intensity events varies significantly depending on the defined relation

Application on Flanders
-----------------------

In this package, example data are presented for Flanders. For applications of
the rainfall erosivity factor in the context of erosion and sediment
transport modelling in Flanders a value of 870
:math:`\frac{\text{MJ.mm}}{\text{ha.h.year}}` is used since 2006
(Verstraeten et al., 2006). Recently, this value has been updated to 1250
:math:`\frac{\text{MJ.mm}}{\text{ha.h.year}}` (Deproost et al., 2018), and has
been evaluated in Gobeyn et al. (in prep).


References
----------

Brown, L.C., Foster, G.R., 1987. Storm erosivity using idealized intensity
distributions. Transactions of the ASAE 30, 0379–0386.
https://doi.org/10.13031/2013.31957

Gobeyn, S., Van de Wauw, J., De Vleeschouwer, N., Renders, D.,
Van Ransbeeck, N., Verstraeten, G., Deproost, P., in prep,  Herziening van de
neerslagerosiviteitsfactor R voor de Vlaamse erosiemodellering.
Departement Omgeving, Brussel, 44 pp.

Renard, K.G., Foster, G.R., Weesies, G.A., McCool, D.K., Yoder, D.C.,
1997, Predicting soil erosion by water: a guide to conservation planning with
the revised universal soil loss equation (RUSLE), Agriculture Handbook. U.S.
Department of Agriculture, Washington.
https://www.ars.usda.gov/ARSUserFiles/64080530/RUSLE/AH_703.pdf

Salles, C., Poesen, J., Pissart, A., 1999, Rain erosivity indices and drop
size distribution for central Belgium. Presented at the General Assembly of
the European Geophysical Society, The Hague, The Netherlands, p. 280.

Salles, C., Poesen, J., Sempere-Torres, D., 2002. Kinetic energy of rain and
its functional relationship with intensity. Journal of Hydrology 257, 256–270.
https://doi.org/10.1016/S0022-1694(01)00555-8

Verstraeten, G., Poesen, J., Demarée, G., Salles, C., 2006, Long-term
(105 years) variability in rain erosivity as derived from 10-min rainfall
depth data for Ukkel (Brussels, Belgium): Implications for assessing soil
erosion rates. Journal Geophysysical Research, 111, D22109.
https://doi.org/10.1029/2006JD007169
