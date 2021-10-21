# quick-moebius

Simple repository for quick implementation of rendering and exploration of limit sets, tiling and orbits of groups and semigroups generated from a finite number of Moebius Transformations.

**Dependencies:**

* `numpy`
* `matplotlib`

**Brief File Description**

* `actual_semiklein.py` - Familiar plug and chug discovery of limit points as implemented in Indra's Pearls (note: dependent on `repetend.py`
* `fast_klein.py` - Python implementation of [Jos Ley's Escape-Time Algorithm for Kleinian Group Limit Sets](http://www.josleys.com/articles/Kleinian%20escape-time_3.pdf)
* `semigroup_leysklein.py` - Adaptation of Jos Ley's algorithm for computing [forward and backward limit sets of Kleinian semigroups](https://arxiv.org/abs/1609.00576)
