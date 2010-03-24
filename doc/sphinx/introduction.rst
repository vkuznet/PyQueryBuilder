Introduction
============

QueryBuilder
DAS stands for Data Aggregation System. It is general purpose
framework to unify data-services into a common layer to be
usable as Google-like interface by end-users. It is developed
for [CMS]_ High Energy Physics experiment at [LHC]_, CERN,
Geneva, Switzerland. Even though it is used so far by CMS
experiment physicists and production tools, its vision
is to have a general purpose architecture applicaple to other
domains.


Dependencies
------------

- *python*, DAS is written in python, see [Python]_;
- *cherrypy*, a generic python web framework, see [CPF]_;
- *yui* the Yahoo YUI Library for building richly interactive web applications,
  see [YUI]_;
- *elementtree* and its *cElementTree* counterpart is used as generic XML parser in DAS,
  both implementations are part of python 2.5 and above;
- *MongoDB* a document-oriented database, the DAS DB back-ends, see [Mongodb]_;
- *pymongo* a MongoDB python driver, see [Pymongo]_;
- *yaml* a human-readable data serialization format, a python YAML library is 
  used for DAS maps and server configurations, see [YAML]_;
- *Cheetah* is python template framework, used for all DAS web tempaltes, see
  [Cheetah]_;
- *sphinx* a python documentation library servers all DAS documentation, 
  see [Sphinx]_;
- *ipython* is an interactive reach python shell (optional, used in some admin tools),
  see [IPython]_;
- *cjson* a C-version of JSON decoder/encoder for python (optinonal), see
  [CJSON]_;

