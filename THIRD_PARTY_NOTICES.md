# Third-party notices

This repository is licensed under the MIT License in [`LICENSE`](LICENSE). It also contains
third-party material, listed here with its own terms.

## nflows

`sfitter/sfitter/fit/rational_quadratic_spline.py` is adapted from
[nflows](https://github.com/bayesiains/nflows) (`nflows/transforms/splines/rational_quadratic.py`
and `nflows/utils/torchutils.py`), distributed under the following license:

```
MIT License

Copyright (c) 2020 Conor Durkan, Artur Bekasov, Iain Murray, George Papamakarios

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## SMEFTatNLO

The image build downloads the SMEFT@NLO UFO model, version 1.0.3, by C. Degrande, G. Durieux,
F. Maltoni, K. Mimasu, E. Vryonidou and C. Zhang, from
<https://feynrules.irmp.ucl.ac.be/wiki/SMEFTatNLO>, checks it against a pinned checksum and
installs it unmodified into MadGraph. It is not part of this repository and not covered by its
`LICENSE`. If you use it, cite [arXiv:2008.11743](https://arxiv.org/abs/2008.11743).

## Software installed when building the image

`image/create_image.sh` downloads and installs third-party software — among others
MadGraph5_aMC@NLO with FastJet, LHAPDF, Pythia8, Ninja and COLLIER, PyTorch, and the SLURM
client — each under its own license. None of it is part of this repository; an image you build
and share bundles those components under their respective terms.
