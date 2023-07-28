# ![Logo Generalizer](icon.png)Generalizer
Generalizer plugin for QGIS 3. Originally written by Piotr Pociask

Plugin to Generalize, Simplify or Smooth lines in QGIS

Functions :
- Remove small objects

- Simplify : 
     * Douglas-Peucker Algorithm
     
     ![Douglas](https://grass.osgeo.org/grass79/manuals/v_generalize_simplify.png "Original line is black")
     
     * Jenk's Algorithm
     * Lang Algorithm
     * Reumann-Witkam Algorithm
     * Vertex Reduction
 
 - Smooth :
     * Boyle's Forward-Looking Algorithm
     
     ![Boyle's](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic15.png/400px-V.generalize.pic15.png "Original line is black")
     
     * Chaikin's Algorithm
     
     ![Chaikin's smooth](https://grass.osgeo.org/grass79/manuals/v_generalize_smooth.png "Original line is black")
     
     ![Chaikin's](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic7.png/400px-V.generalize.pic7.png "Original is black")
     
     * Hermite Spline Interpolation
     
     ![Hermite](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic8.png/400px-V.generalize.pic8.png "Original is black")
     
     ![Hermite and Chaikin](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic9.png/400px-V.generalize.pic9.png "Original = black, Green = Chaikin, Blue = Hermite")
     
     * McMaster's Distance-Weighting Algorithm
     
     ![Distance Weighting](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic13.png/400px-V.generalize.pic13.png "Original line is black")
     
     * McMaster's Sliding Averaging Algorithm
     
     ![Sliding](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic11.png/400px-V.generalize.pic11.png "Original line is black")
     
     ![Sliding2](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic12.png/400px-V.generalize.pic12.png "Original line is black")
     
     * Snakes Algorithm :
     Slowest smoothing algorithm
     
     ![Snakes](https://grasswiki.osgeo.org/w/images/thumb/V.generalize.pic14.png/400px-V.generalize.pic14.png "Original line is black")
     
     

Which algorithm to choose : https://grasswiki.osgeo.org/wiki/V.generalize_tutorial
