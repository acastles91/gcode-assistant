G4 P2000
M204 S50

;beginning
G1 X-425 Y405 F2000
G1 X-420 Y425 F2000
G1 X-100 Y-100 F2000

;1st row right, second left, third right, fourth left
G1 X60 Y150 F2000

;swipe
G0 X408 Y-400 F2500
G0 X-410 Y400 F2500
G0 X300 Y-300 F2500
G0 X210 Y-211 F400
G0 X-335 Y-340 F1500

;dump
;G4 P4000

;rewind
G4 P700
G0 X680 Y-5 F1500
G0 X-850 Y-75 F2000
G0 X882 Y51 F3000

SET_KINEMATIC_POSITION X=0 Y=0 Z=0
;
;limits
;Y915 
