UNICEF IoGT
===========


Custom version of [Molo IoGT](https://github.com/praekeltfoundation/molo-iogt).





Configure image
---------------

Following optional environment are required:

    # Docker molo base image
    MOLO_VERSION=6   
    # IoGT tag or commit to use as codebase
    IOGT_VERSION=a6e3f08
    
These variables are already set in the Makefile to the last released build.

   
     
Build, Test and publish the image on GitHub
-------------------------------------

    make build  
    make test 
    make release

or

    make build test release
    
    
#### Note
    
Do not forget to bump version after each release, we use [bumpversion](https://github.com/peritus/bumpversion) to achieve that    


    bumpversion minor
