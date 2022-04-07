
    Point(1) = {0, 0, 0, 0.5 };
    Point(2) = { 6.0, 0, 0, 0.5 };
    Point(3) = { 6.0, 4.0, 0, 0.5 };
    Point(4) = { 0,   4.0, 0, 0.5 };
    Point(5) = { 0,   2.25, 0, 0.001953125 };
    Point(6) = { 2.0,   2.0, 0, 0.001953125 };
    Point(7) = { 0,   1.75, 0, 0.001953125 };
    
    Line(1) = {1, 2};
    Line(2) = {2, 3};
    Line(3) = {3, 4};
    Line(4) = {4, 5};
    Line(5) = {5, 6};
    Line(6) = {6, 7};
    Line(7) = {7, 1};
    Line Loop(8) = {1, 2, 3, 4, 5, 6, 7};
    Plane Surface(9) = {8};
    
    Physical Surface(10) = {9};
    Physical Line("XBlocked") = {2};
    Physical Line("YBlocked") = {1};
    Physical Line("Traction") = {3};
    