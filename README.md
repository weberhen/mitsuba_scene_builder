# mitsuba_scene_builder

Render your scenes in mitsuba without a XML file.

An example of configuration file (JSON file) and a simple scene in XML format can be found in the example folder.
To render the scene described by these two files, simply run

    python main.py -b example/scene.xml -c example/config.json
   
Dependencies
============

 * [Mitsuba](http://http://mitsuba-renderer.org/) 
 
If you want to render using the [MERL](http://people.csail.mit.edu/wojciech/BRDFDatabase/) database, you will also need:
 * [ALTA](http://alta.gforge.inria.fr/)
 * [AltaBRDF](https://github.com/belcour/AltaBRDF)
  
Virtual Point Lights File
=========================

This file is created by [EnvyDepth](http://vcg.isti.cnr.it/Publications/2013/BCDCPS13/)

Example of a file with 4 virtual point lights and their position, normal, color and scale
    
    NVPLS: 4
    pos_0 0.004710 2.400000 0.000000
    nor_0 -0.004703 -0.999989 -0.000000
    col_0 0.048049 0.031343 0.011285
    scale_0: 1.000022
    pos_1 0.004710 2.400000 0.000022
    nor_1 -0.004703 -0.999989 -0.000022
    col_1 0.048042 0.031351 0.011300
    scale_1: 1.000022
    pos_2 0.004710 2.400000 0.000044
    nor_2 -0.004703 -0.999989 -0.000044
    col_2 0.048037 0.031351 0.011320
    scale_2: 1.000022
    pos_3 0.004710 2.400000 0.000067
    nor_3 -0.004702 -0.999989 -0.000066
    col_3 0.048040 0.031363 0.011345
    scale_3: 1.000022



