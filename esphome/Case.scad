// ========================================================
// STYLED SIDE-CAR XIAO ESP32-C3 + DHT11 + ANTENNA ENCLOSURE
// Features: Full-Height Antenna Bay, 3D Chamfering, Cooling Ribs
// ========================================================

wall = 2;
floor = 2;
lid_thickness = 2.5; // Slightly thicker for styling
tolerance = 0.4; 
divider = 1.5;
lip_depth = 3;
lip_clearance = 0.2;
chamfer_size = 1.5;
antenna_width = 10; 

eps = 0.05; 
$fn=40;

// ==============================
// COMPONENT SIZING
// ==============================
xiao_x = 21;
xiao_y = 17.5;
xiao_z = 7; 

dht_x = 26;
dht_y = 16;
dht_z = 12;

xiao_inner_x = xiao_x + tolerance*2;
xiao_inner_y = xiao_y + tolerance*2;
dht_inner_x = dht_x + 1;
dht_inner_y = dht_y + 1;

outer_x = xiao_inner_x + dht_inner_x + divider + wall*2;
outer_y = max(xiao_inner_y, dht_inner_y) + antenna_width + divider + wall*2;
// Height is driven by the DHT11 + floor + room for wires/lid
outer_z = dht_z + floor + 3; 

// ==============================
// STYLING UTILITIES
// ==============================

// Creates the 2D footprint with corner chamfers
module profile_2d(x, y, c) {
    polygon([[c,0],[x-c,0],[x,c],[x,y-c],[x-c,y],[c,y],[0,y-c],[0,c]]);
}

// 3D Chamfered Box (Beveled on all outside edges)
module styled_box(x, y, z, c) {
    hull() {
        // Bottom layer
        translate([0,0,0.1]) linear_extrude(height=0.1) profile_2d(x,y,c);
        // Middle layer
        translate([0,0,c]) linear_extrude(height=z-c*2) profile_2d(x,y,c);
        // Top layer
        translate([0,0,z-0.1]) linear_extrude(height=0.1) profile_2d(x,y,c);
        
        // This hull approach creates a 45-degree bevel on the top/bottom edges
        // as well as the vertical corners.
    }
}

// ==============================
// MAIN CASE
// ==============================
module combined_case() {
    difference() {
        // Styled Outer Shell
        styled_box(outer_x, outer_y, outer_z, chamfer_size);

        // 1. XIAO CAVITY
        translate([wall, wall, floor])
            cube([xiao_inner_x, xiao_inner_y, outer_z]);

        // 2. DHT11 CAVITY
        translate([wall + xiao_inner_x + divider, wall, floor])
            cube([dht_inner_x, dht_inner_y, outer_z]);

        // 3. ANTENNA "SIDE-CAR" (Full Height)
        translate([wall, outer_y - wall - antenna_width, floor])
            cube([outer_x - wall*2, antenna_width, outer_z]);

        // USB-C PORT
        translate([-eps, wall + xiao_inner_y/2 - 5, floor + 1])
            cube([wall + 2*eps, 10, 6]);

        // --- CABLE ROUTING ---
        
        // ANTENNA CABLE (Floor Level)
        translate([wall + xiao_inner_x/2, wall + xiao_inner_y - eps, floor])
            cube([11, divider + 2*eps, 4]); 
            
        // MAIN WIRING (Xiao to DHT11)
        translate([wall + xiao_inner_x - eps, wall + 4, floor])
            cube([divider + 2*eps, 8, 8]);

        // VENTILATION SLOTS (On the DHT end)
        for(i=[0:2])
            translate([outer_x - wall - eps, wall + 4 + i*4, floor + 4])
                cube([wall + 2*eps, 2, 7]);

        // SNAP GROOVES (Long sides)
        translate([outer_x/2, wall, outer_z - lip_depth/2])
            rotate([0,90,0]) cylinder(r=0.6, h=outer_x-wall*4, center=true);
        translate([outer_x/2, outer_y - wall, outer_z - lip_depth/2])
            rotate([0,90,0]) cylinder(r=0.6, h=outer_x-wall*4, center=true);
            
        // RECESS FOR LID LIP
        translate([wall + 1, wall + 1, outer_z - lip_depth])
            cube([outer_x - wall*2 - 2, outer_y - wall*2 - 2, lip_depth + eps]);
    }
}

// ==============================
// LID
// ==============================
module combined_lid() {
    lip_x = outer_x - wall*2 - lip_clearance*2;
    lip_y = outer_y - wall*2 - lip_clearance*2;
    
    union() {
        // Styled Lid Top
        difference() {
            styled_box(outer_x, outer_y, lid_thickness, chamfer_size);
            
            // "Styling" - Decorative cooling ribs/grip slots on top
            for(i=[0:6]) {
                translate([wall + 5 + i*6, wall, lid_thickness - 1])
                    cube([2, outer_y - wall*2, 2]);
            }
        }

        // Snap Lip
        translate([wall + lip_clearance, wall + lip_clearance, -lip_depth])
            cube([lip_x, lip_y, lip_depth]);

        // Snap Ridges
        translate([outer_x/2, wall + lip_clearance, -lip_depth/2])
            rotate([0,90,0]) cylinder(r=0.5, h=lip_x-4, center=true);
        translate([outer_x/2, outer_y - wall - lip_clearance, -lip_depth/2])
            rotate([0,90,0]) cylinder(r=0.5, h=lip_x-4, center=true);
    }
}

// ==============================
// RENDER
// ==============================
combined_case();

// Lid translated and flipped for print orientation
translate([0, outer_y + 40, lid_thickness]) 
    rotate([180,0,0]) translate([0,0,-lid_thickness]) 
    combined_lid();