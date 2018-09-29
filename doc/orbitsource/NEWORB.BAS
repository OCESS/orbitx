1111    ON ERROR GOTO 9000
        SCREEN 12
        PALETTE 8, 19 + (19 * 256) + (19 * 65536)
        DEFDBL A-Z
        DIM P(40, 11), Px(40, 5), Py(40, 5), Vx(40), Vy(40), B(1, 250), Ztel(33), Znme$(42)
        DIM Pz(3021, 2) AS SINGLE
91      OPEN "I", #1, "starsr"
        FOR i = 1 TO 3021
         INPUT #1, Pz(i, 0)
         INPUT #1, Pz(i, 1)
         INPUT #1, Pz(i, 2)
        NEXT i
        FOR i = 1 TO 241
         INPUT #1, B(0, i)
         INPUT #1, B(1, i)
        NEXT i
        FOR i = 0 TO 39
         INPUT #1, P(i, 0)
         INPUT #1, P(i, 4)
         INPUT #1, P(i, 5)
         INPUT #1, P(i, 8)
         INPUT #1, P(i, 9)
         INPUT #1, P(i, 10)
        NEXT i
        INPUT #1, year, day, hr, min, sec
        FOR i = 0 TO 35
         INPUT #1, Px(i, 3), Py(i, 3), Vx(i), Vy(i), P(i, 1), P(i, 2)
        NEXT i
        FOR i = 0 TO 39
         INPUT #1, Znme$(i)
        NEXT i
        Znme$(40) = "TARGET"
        Znme$(42) = " Vtg"
        Znme$(41) = " Pch"
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        CLOSE #1

     
        'System variables
99      eng = 0:    vflag = 0:  Aflag = 0:   Sflag = 0
        mag = 25:   Sangle = 0: cen = 0:     targ = 0:   ref = 3
        trail = 1:  tr = 0:     dte = 0:     ts = .25:   Eflag = 0
        AYSEangle = 0: AYSEscrape = 0: HABrotate% = 0
        master = 0
        MODULEflag = 0
        fuel = 2000
        AYSEfuel = 15120000
        AU = 149597890000#
        RAD = 57.295779515#
        G = 6.673E-11
        pi = 3.14159
        pi2 = 2 * pi
        Px(0, 3) = 0
        Py(0, 3) = 0
        Vx(0) = 0
        Vy(0) = 0
        P(0, 1) = 0
        P(0, 2) = 0
        vernP! = -100
        OLDts = .25
       
        'Forced situation file
80      OPEN "I", #1, "orbitstr.txt"
        INPUT #1, suA$
        CLOSE #1
        IF UCASE$(suA$) = "NORMAL" THEN 51
        z$ = suA$
        GOTO 52

51      LOCATE 5, 5
        PRINT "ORBIT v. 5t"
        PRINT
        INPUT "    Do you wish to reload the last timed backup: ", z$
        IF UCASE$(z$) = "YES" OR UCASE$(z$) = "Y" THEN z$ = "OSBACKUP"
52      IF z$ <> "" THEN filename$ = z$: GOSUB 704
        CLS
        GOSUB 400

        'Initialize frame rate timer
100     tttt = TIMER
        'GOTO 9111
       
        'Zero acceleration variables
        FOR i = 0 TO 35: P(i, 1) = 0: P(i, 2) = 0: NEXT i
        P(38, 1) = 0
        P(38, 2) = 0
        P(39, 1) = 0
        P(39, 2) = 0
       
        'Erase target vector
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (20 * SIN(Atarg)), 120 + (20 * COS(Atarg))), 0
        IF SQR(((Px(28, 3) - cenX) * mag / AU) ^ 2 + ((Py(28, 3) - cenY) * mag * 1 / AU) ^ 2) > 400 THEN 131
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (30 * SIN(Atarg)) + (Px(28, 3) - cenX) * mag / AU, 220 + (30 * COS(Atarg)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (10 * SIN(Sangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (10 * COS(Sangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
        
131     CONflag = 0
        atm = 40
        LtrA = 0
        'Calculate gravitational acceleration for each object pair
        FOR i = 1 TO 166 + (ufo1 * 38) + (ufo2 * 37)
         IF B(1, i) = B(0, i) THEN 106
         IF B(1, i) = 32 AND AYSE = 150 THEN 106
         difX = Px(B(1, i), 3) - Px(B(0, i), 3)
         difY = Py(B(1, i), 3) - Py(B(0, i), 3)
         GOSUB 5000
         r = SQR((difY ^ 2) + (difX ^ 2))
         IF r < .01 THEN 106
         a = G * P(B(0, i), 4) / (r ^ 2)
         P(B(1, i), 1) = P(B(1, i), 1) + (a * SIN(angle))
         P(B(1, i), 2) = P(B(1, i), 2) + (a * COS(angle))
         IF B(1, i) = 32 AND r <= P(B(0, i), 5) + P(32, 5) THEN CONflag2 = 1: CONflag3 = B(0, i): targ = 32
         IF B(1, i) = 28 AND P(B(0, i), 10) > -150 AND r <= P(B(0, i), 5) + P(28, 5) THEN CONflag = 1: CONtarg = B(0, i): Dcon = r: Acon = angle: CONacc = a
         IF B(1, i) = 28 AND B(0, i) <> 32 AND r <= P(B(0, i), 5) + (1000 * P(B(0, i), 10)) THEN atm = B(0, i): Ratm = (r - P(B(0, i), 5)) / 1000
         IF B(1, i) = 39 AND r <= P(B(0, i), 5) + P(39, 5) THEN explCENTER = 39: GOSUB 6000
         IF B(1, i) = 38 AND r <= P(B(0, i), 5) + P(38, 5) THEN explCENTER = 38: GOSUB 6000
         IF B(0, i) = ref AND B(1, i) = 28 THEN Vref = SQR(G * P(B(0, i), 4) / r): Aref = angle: Dref = r
         IF B(0, i) = targ AND B(1, i) = 28 THEN Atarg = angle: Dtarg = r: Acctarg = a
         IF B(0, i) = Ltr THEN LtrA = a
         IF i = 163 THEN AYSEdist = r
         IF i = 166 THEN OCESSdist = r
106     NEXT i
        IF AYSEdist > 320 THEN AYSE = 0
        'IF CONflag = 1 AND CONtarg = 14 THEN 9111

        'Record old center position
101     cenX = Px(cen, 3) + cenXoff
        cenY = Py(cen, 3) + cenYoff
       
        'Erase velocity, approach velocity, and orientation vectors
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (5 * SIN(Sangle)), 120 + (5 * COS(Sangle))), 0
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (10 * SIN(Vvangle)), 120 + (10 * COS(Vvangle))), 0
        IF SQR(((Px(28, 3) - cenX) * mag / AU) ^ 2 + ((Py(28, 3) - cenY) * mag * 1 / AU) ^ 2) > 400 THEN 132
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (20 * SIN(Vvangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (20 * COS(Vvangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
       
        'Update object velocities and erase old positions
132     FOR i = 37 + ufo1 + ufo2 TO 0 STEP -1
         IF i = 28 THEN GOSUB 301
         IF i = 38 THEN GOSUB 7200
         Vx(i) = Vx(i) + (P(i, 1) * OLDts)
         Vy(i) = Vy(i) + (P(i, 2) * OLDts)
117      IF i = 36 AND MODULEflag = 0 THEN 108
         IF SQR(((Px(i, 3) - cenX) * mag / AU) ^ 2 + ((Py(i, 3) - cenY) * mag * 1 / AU) ^ 2) - (P(i, 5) * mag / AU) > 400 THEN 108
         IF cen * tr > 0 THEN 108
         IF mag * P(i, 5) / AU > 3200 THEN 118
         IF mag * P(i, 5) / AU < 1.1 THEN PSET (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag / AU), 8 * trail: GOTO 108
         clr = 8 * trail
         IF i = 28 THEN vnSa = oldSa: GOSUB 128: GOTO 108
         IF i = 35 THEN GOSUB 138: GOTO 108
         IF i = 37 THEN GOSUB 148: GOTO 108
         IF i = 32 THEN clrMASK = 0: GOSUB 158: GOTO 108
         CIRCLE (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), mag * P(i, 5) / AU, 8 * trail: GOTO 108

118      difX = Px(i, 3) - cenX
         difY = Py(i, 3) - cenY
         dist = (SQR((difY ^ 2) + (difX ^ 2)) - P(i, 5)) * mag / AU
         GOSUB 5000
         csz = COS(angle - 1.5707964#)
         snz = SIN(angle - 1.5707964#)
         LINE (300 - (dist * csz) - (300 * snz), 220 + (dist * snz) - (300 * csz))-(300 - (dist * csz) + (300 * snz), 220 + (dist * snz) + (300 * csz)), 8 * trail
108     NEXT i
        GOTO 102

         'Paint Habitat
128      CIRCLE (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), mag * P(i, 5) / AU, clr
         CIRCLE (300 + (Px(i, 3) - cenX - (P(i, 5) * .8 * SIN(vnSa))) * mag / AU, 220 + (Py(i, 3) - cenY - (P(i, 5) * .8 * COS(vnSa))) * mag * 1 / AU), mag * P(i, 5) * .2 / AU, clr
         CIRCLE (300 + (Px(i, 3) - cenX - (P(i, 5) * 1.2 * SIN(vnSa + .84))) * mag / AU, 220 + (Py(i, 3) - cenY - (P(i, 5) * 1.2 * COS(vnSa + .84))) * mag * 1 / AU), mag * P(i, 5) * .2 / AU, clr
         CIRCLE (300 + (Px(i, 3) - cenX - (P(i, 5) * 1.2 * SIN(vnSa - .84))) * mag / AU, 220 + (Py(i, 3) - cenY - (P(i, 5) * 1.2 * COS(vnSa - .84))) * mag * 1 / AU), mag * P(i, 5) * .2 / AU, clr
         RETURN

         'Paint ISS
138      LINE (300 + (Px(i, 3) - cenX - 450) * mag / AU, 220 + (Py(i, 3) - cenY - 150) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 450) * mag / AU, 220 + (Py(i, 3) - cenY + 150) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX + 500) * mag / AU, 220 + (Py(i, 3) - cenY + 25) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 450) * mag / AU, 220 + (Py(i, 3) - cenY - 25) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX - 500) * mag / AU, 220 + (Py(i, 3) - cenY + 25) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX - 450) * mag / AU, 220 + (Py(i, 3) - cenY - 25) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX - 350) * mag / AU, 220 + (Py(i, 3) - cenY + 200) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 350) * mag / AU, 220 + (Py(i, 3) - cenY + 355) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX - 350) * mag / AU, 220 + (Py(i, 3) - cenY - 200) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 350) * mag / AU, 220 + (Py(i, 3) - cenY - 355) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX - 50) * mag / AU, 220 + (Py(i, 3) - cenY + 200) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 50) * mag / AU, 220 + (Py(i, 3) - cenY + 150) * mag * 1 / AU), clr, B
         LINE (300 + (Px(i, 3) - cenX - 50) * mag / AU, 220 + (Py(i, 3) - cenY - 200) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + 50) * mag / AU, 220 + (Py(i, 3) - cenY - 150) * mag * 1 / AU), clr, B
         RETURN

         'Paint OCESS
148      px1 = ((Px(37, 3) + 97.5305) - cenX) * mag / AU: py1 = ((Py(37, 3) + 69.2462) - cenY) * mag / AU
         px2 = ((Px(37, 3) + 69.2462) - cenX) * mag / AU: py2 = ((Py(37, 3) + 97.5305) - cenY) * mag / AU
         px3 = ((Px(37, 3) + 21.2132) - cenX) * mag / AU: py3 = ((Py(37, 3) - 21.2132) - cenY) * mag / AU
         px4 = ((Px(37, 3) - 21.2132) - cenX) * mag / AU: py4 = ((Py(37, 3) + 21.2132) - cenY) * mag / AU
         px5 = ((Px(37, 3) - 55.1041) - cenX) * mag / AU: py5 = ((Py(37, 3) - 111.6726) - cenY) * mag / AU
         px6 = ((Px(37, 3) - 111.6726) - cenX) * mag / AU: py6 = ((Py(37, 3) - 55.1041) - cenY) * mag / AU
         LINE (300 + px1, 220 + py1)-(300 + px5, 220 + py5), clr
         LINE (300 + px5, 220 + py5)-(300 + px6, 220 + py6), clr
         LINE (300 + px6, 220 + py6)-(300 + px2, 220 + py2), clr
         LINE (300 + px2, 220 + py2)-(300 + px1, 220 + py1), clr
         LINE (300 + px1, 220 + py1)-(300 + px4, 220 + py4), clr
         LINE (300 + px4, 220 + py4)-(300 + px5, 220 + py5), clr
         LINE (300 + px6, 220 + py6)-(300 + px3, 220 + py3), clr
         LINE (300 + px3, 220 + py3)-(300 + px2, 220 + py2), clr
         RETURN
      
         'Paint AYSE
158      angleS = AYSEangle + 1.785
         IF angleS > pi2 THEN angleS = angleS - pi2
         IF angleS < 0 THEN angleS = angleS + pi2
    
         angleE = AYSEangle + 1.36
         IF angleE > pi2 THEN angleE = angleE - pi2
         IF angleE < 0 THEN angleE = angleE + pi2

         angleS1 = AYSEangle - pi
         IF angleS1 > pi2 THEN angleS1 = angleS1 - pi2
         IF angleS1 < 0 THEN angleS1 = angleS1 + pi2
      
         angleE1 = AYSEangle
         IF angleE1 > pi2 THEN angleE1 = angleE1 - pi2
         IF angleE1 < 0 THEN angleE1 = angleE1 + pi2

         Ax1 = Px(32, 3) + (500 * SIN(AYSEangle + .19 + pi))
         Ax2 = Px(32, 3) + (500 * SIN(AYSEangle - .19 + pi))
         Ay1 = Py(32, 3) + (500 * COS(AYSEangle + .19 + pi))
         Ay2 = Py(32, 3) + (500 * COS(AYSEangle - .19 + pi))
         Ax3 = Px(32, 3) + (95 * SIN(AYSEangle + (pi / 2)))
         Ax4 = Px(32, 3) + (95 * SIN(AYSEangle - (pi / 2)))
         Ay3 = Py(32, 3) + (95 * COS(AYSEangle + (pi / 2)))
         Ay4 = Py(32, 3) + (95 * COS(AYSEangle - (pi / 2)))
       
         Ax5 = Ax1 - (1000 * SIN(AYSEangle))
         Ay5 = Ay1 - (1000 * COS(AYSEangle))
         IF Ax1 = Ax5 THEN Ad1 = ABS(Px(28, 3) - Ax1): GOTO 157
         IF Ay1 = Ay5 THEN Ad1 = ABS(Py(28, 3) - Ay1): GOTO 157
         Am1 = (Ay1 - Ay5) / (Ax1 - Ax5)
         Am11 = -1 * (Ax1 - Ax5) / (Ay1 - Ay5)
         Ab1 = Ay1 - (Am1 * Ax1)
         Ab11 = Py(28, 3) - (Am11 * Px(28, 3))
         Ax7 = (Ab11 - Ab1) / (Am1 - Am11)
         Ay7 = (Am1 * Ax7) + Ab1
         Ad1 = SQR((Px(28, 3) - Ax7) ^ 2 + (Py(28, 3) - Ay7) ^ 2)

157      Ax6 = Ax2 - (1000 * SIN(AYSEangle))
         Ay6 = Ay2 - (1000 * COS(AYSEangle))
         IF Ax2 = Ax6 THEN Ad2 = ABS(Px(28, 3) - Ax2): GOTO 159
         IF Ay2 = Ay6 THEN Ad2 = ABS(Py(28, 3) - Ay2): GOTO 159
         Am2 = (Ay2 - Ay6) / (Ax2 - Ax6)
         Am22 = -1 * (Ax2 - Ax6) / (Ay2 - Ay6)
         Ab2 = Ay2 - (Am2 * Ax2)
         Ab22 = Py(28, 3) - (Am22 * Px(28, 3))
         Ax8 = (Ab22 - Ab2) / (Am2 - Am22)
         Ay8 = (Am2 * Ax8) + Ab2
         Ad2 = SQR((Px(28, 3) - Ax8) ^ 2 + (Py(28, 3) - Ay8) ^ 2)
        
159      Ad3 = SQR((Px(28, 3) - Ax1) ^ 2 + (Py(28, 3) - Ay1) ^ 2)
         clr1 = 4
         clr2 = 4
         IF Ad1 > 90 AND Ad2 < 200 THEN clr1 = 14
         IF Ad2 > 90 AND Ad1 < 200 THEN clr2 = 14
         IF Ad1 > 92 AND Ad2 < 200 THEN clr1 = 2
         IF Ad2 > 92 AND Ad1 < 200 THEN clr2 = 2
         IF ABS(Ad1 - 94.4) < 6 AND ABS(Ad2 - 94.4) < 6 AND Ad3 < 510 THEN CONflag = 0:  GOTO 156
         IF AYSEdist > 580 THEN 156
         AYSEscrape = 10
         Vx(28) = Vx(32)
         Vy(28) = Vy(32)
         P(28, 1) = P(32, 1)
         P(28, 2) = P(32, 2)
         IF ABS(Ad1 - 94.4) > 8 AND ABS(Ad2 - 94.4) > 8 OR Ad3 > 515 THEN 156
         Px(28, 3) = (Ax8 + Ax7) / 2
         Py(28, 3) = (Ay8 + Ay7) / 2
         IF Ad3 > 510 THEN Px(28, 3) = Px(32, 3): Py(28, 3) = Py(32, 3)
         CLS
         GOSUB 400
         CONflag = 0

156      IF AYSEdist < 5 THEN clr = 10 ELSE clr = 12
         CIRCLE (300 + ((Px(32, 3) - cenX) * mag / AU), 220 + ((Py(32, 3) - cenY) * mag / AU)), 95 * mag / AU, clr * clrMASK, angleS1, angleE1
         LINE (300 + ((Ax1 - cenX) * mag / AU), 220 + ((Ay1 - cenY) * mag / AU))-(300 + ((Ax4 - cenX) * mag / AU), 220 + ((Ay4 - cenY) * mag / AU)), 12 * clrMASK
         LINE (300 + ((Ax2 - cenX) * mag / AU), 220 + ((Ay2 - cenY) * mag / AU))-(300 + ((Ax3 - cenX) * mag / AU), 220 + ((Ay3 - cenY) * mag / AU)), 12 * clrMASK
         IF AYSE < 150 THEN CIRCLE (300 + ((Px(32, 3) - cenX) * mag / AU), 220 + ((Py(32, 3) - cenY) * mag / AU)), 500 * mag / AU, 12 * clrMASK, angleS, angleE ELSE CIRCLE (300 + ((Px(32, 3) - cenX) * mag / AU), 220 + ((Py(32, 3) - cenY) * mag / AU) _
), 500 * mag / AU, 12 * clrMASK
         Ax10 = 300 + ((Ax1 - cenX) * mag / AU)
         Ay10 = 220 + ((Ay1 - cenY) * mag / AU)
         IF mag < 5E+09 THEN 154
         LINE (Ax10 - 1, Ay10 - 1)-(Ax10 + 1, Ay10 + 1), clr1 * clrMASK, BF
         CIRCLE (Ax10, Ay10), 2, clr1 * clrMASK
154      Ax10 = 300 + ((Ax2 - cenX) * mag / AU)
         Ay10 = 220 + ((Ay2 - cenY) * mag / AU)
         IF mag < 5E+09 THEN 153
         LINE (Ax10 - 1, Ay10 - 1)-(Ax10 + 1, Ay10 + 1), clr2 * clrMASK, BF
         CIRCLE (Ax10, Ay10), 2, clr2 * clrMASK
153      RETURN


        'Detect contact with an object
102     explFLAG1 = 0
        IF CONflag = 0 THEN 112
        vector = COS(THRUSTangle - Acon)
        IF CONtarg > 37 THEN ufo2 = 0: explFLAG1 = 1: eng = 0: targ = ref: GOTO 112
        IF ((Dcon - P(CONtarg, 5) - P(28, 5)) <= 0) AND ((Aacc + Av + Are) * vector < CONacc * 1.01) THEN Vx(28) = Vx(CONtarg): Vy(28) = Vy(CONtarg)
        IF vector >= 0 THEN 193
         Pvx = P(CONtarg, 4)
         IF Pvx < 1 THEN Pvx = 1
         Vx(CONtarg) = Vx(CONtarg) + (THRUSTx * ts * HABmass / Pvx): Vx(28) = Vx(CONtarg)
         Vy(CONtarg) = Vy(CONtarg) + (THRUSTy * ts * HABmass / Pvx): Vy(28) = Vy(CONtarg)
193     IF ((Dcon - P(CONtarg, 5) - P(28, 5)) > -.5) THEN GOTO 112
        eng = 0
        Px(28, 3) = Px(CONtarg, 3) + ((P(CONtarg, 5) + P(28, 5) - .1) * SIN(Acon + 3.1415926#))
        Py(28, 3) = Py(CONtarg, 3) + ((P(CONtarg, 5) + P(28, 5) - .1) * COS(Acon + 3.1415926#))
        explFLAG1 = 1



        'Docked with AYSE drive module
112     explFLAG2 = 0
        IF AYSE = 150 THEN Vx(32) = Vx(28): Vy(32) = Vy(28): Px(32, 3) = Px(28, 3): Py(32, 3) = Py(28, 3): AYSEangle = Sangle
        IF CONflag2 = 1 AND CONflag4 = 0 THEN CONflag4 = 1: explFLAG2 = 1
        IF CONflag2 = 1 AND CONflag3 < 38 THEN Vx(32) = Vx(CONflag3): Vy(32) = Vy(CONflag3)
       
       
        'Update object positions
        FOR i = 0 TO 37 + ufo1 + ufo2
         Px(i, 3) = Px(i, 3) + (Vx(i) * ts)
         Py(i, 3) = Py(i, 3) + (Vy(i) * ts)
        NEXT i


        IF ts > 10 THEN GOSUB 3100
        IF MODULEflag > 0 THEN Px(36, 3) = P(36, 1) + Px(MODULEflag, 3): Py(36, 3) = P(36, 2) + Py(MODULEflag, 3): Vx(36) = Vx(MODULEflag): Vy(36) = Vy(MODULEflag)
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
       
        'Record new center position
        cenX = Px(cen, 3) + cenXoff
        cenY = Py(cen, 3) + cenYoff
     
       
        'Repaint objects to the screen
111     FOR i = 37 + ufo1 + ufo2 TO 0 STEP -1
         IF i = 36 AND MODULEflag = 0 THEN 109
         IF SQR(((Px(i, 3) - cenX) * mag / AU) ^ 2 + ((Py(i, 3) - cenY) * mag * 1 / AU) ^ 2) - (P(i, 5) * mag / AU) > 400 THEN 109
         IF mag * P(i, 5) / AU > 3200 THEN 119
         pld = 0
         IF i = 28 THEN pld = 2 * ABS(SGN(eng))
         IF mag * P(i, 5) / AU < 1.1 THEN PSET (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), P(i, 0) + pld: GOTO 109
         IF i = 28 THEN clr = 12 + pld: vnSa = Sangle: GOSUB 128: GOTO 109
         IF i = 35 THEN clr = 12: GOSUB 138: GOTO 109
         IF i = 37 THEN clr = 12: GOSUB 148: GOTO 109
         IF i = 32 THEN clrMASK = 1: GOSUB 158: GOTO 109
         CIRCLE (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), mag * P(i, 5) / AU, P(i, 0) + pld: GOTO 109

119      difX = Px(i, 3) - cenX
         difY = Py(i, 3) - cenY
         dist = (SQR((difY ^ 2) + (difX ^ 2)) - P(i, 5)) * mag / AU
         GOSUB 5000
         csz = COS(angle - 1.5707964#)
         snz = SIN(angle - 1.5707964#)
         LINE (300 - (dist * csz) - (300 * snz), 220 + (dist * snz) - (300 * csz))-(300 - (dist * csz) + (300 * snz), 220 + (dist * snz) + (300 * csz)), P(i, 0)

109     NEXT i
       

        'Calculate parameters for landing target
        IF targ < 40 THEN 179
        IF SQR(((Px(40, 3) - cenX) * mag / AU) ^ 2 + ((Py(40, 3) - cenY) * mag * 1 / AU) ^ 2) < 401 THEN PSET (300 + (Px(40, 3) - cenX) * mag / AU, 220 + (Py(40, 3) - cenY) * mag * 1 / AU), 8 * trail
        Px(40, 3) = Px(Ltr, 3) + Ltx
        Py(40, 3) = Py(Ltr, 3) + Lty
        IF SQR(((Px(40, 3) - cenX) * mag / AU) ^ 2 + ((Py(40, 3) - cenY) * mag * 1 / AU) ^ 2) < 401 THEN PSET (300 + (Px(40, 3) - cenX) * mag / AU, 220 + (Py(40, 3) - cenY) * mag * 1 / AU), 15
        Vx(40) = Vx(Ltr)
        Vy(40) = Vy(Ltr)
        difX = Px(28, 3) - Px(40, 3)
        difY = Py(28, 3) - Py(40, 3)
        Dtarg = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        Atarg = angle
        IF Dtarg = 0 THEN 179
        Acctarg = LtrA + ((((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2) / (2 * (Dtarg))))

179     oldSa = Sangle
     
        'Calculate angle from target to reference object
        IF targ = ref THEN Atargref = 0: GOTO 114
        difX = Px(targ, 3) - Px(ref, 3)
        difY = Py(targ, 3) - Py(ref, 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        Atr = angle
        Atargref = ABS(angle - Aref)
        IF Atargref > 3.1415926535# THEN Atargref = 6.283185307# - Atargref


        'Re-paint target vector
114     IF DISPflag = 0 THEN LINE (30, 120)-(30 + (20 * SIN(Atarg)), 120 + (20 * COS(Atarg))), 8
       
       
        'Repaint velocity and orientation vectors
        difX = Vx(targ) - Vx(28)
        difY = Vy(targ) - Vy(28)
        GOSUB 5000
        Vvangle = angle
               
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (10 * SIN(Vvangle)), 120 + (10 * COS(Vvangle))), 12
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (5 * SIN(Sangle)), 120 + (5 * COS(Sangle))), 10
        IF DISPflag = 0 THEN PSET (30, 120), 1
        IF SQR(((Px(28, 3) - cenX) * mag / AU) ^ 2 + ((Py(28, 3) - cenY) * mag * 1 / AU) ^ 2) > 400 THEN 133
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (30 * SIN(Atarg)) + (Px(28, 3) - cenX) * mag / AU, 220 + (30 * COS(Atarg)) + (Py(28, 3) - cenY) * mag * 1 / AU), 8
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (20 * SIN(Vvangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (20 * COS(Vvangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 12
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (10 * SIN(Sangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (10 * COS(Sangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 10
133     VangleDIFF = Atarg - Vvangle
       
       
        'Cause explosion
        IF Ztel(5) = 1 THEN Ztel(5) = 0: explFLAG1 = 1: explosion = 0
        IF Ztel(6) = 1 THEN Ztel(6) = 0: explFLAG2 = 1: explosion1 = 0
        IF explFLAG1 = 1 AND explosion = 0 THEN explCENTER = 28: GOSUB 6000
        IF explFLAG2 = 1 AND explosion1 = 0 THEN explCENTER = 32: GOSUB 6000


        'Update simulation time
        sec = sec + ts
        IF sec > 60 THEN min = min + 1: sec = sec - 60
        IF min = 60 THEN hr = hr + 1: min = 0
        IF hr = 24 THEN day = day + 1: hr = 0
        dayNUM = 365
        IF INT(year / 4) * 4 = year THEN dayNUM = 366
        IF INT(year / 100) * 100 = year THEN dayNUM = 365
        IF INT(year / 400) * 400 = year THEN dayNUM = 366
        IF day = dayNUM + 1 THEN year = year + 1: day = 1
       
        IF dte = 0 THEN 121
        IF dte > 1 THEN GOSUB 8100: GOTO 121
        LOCATE 25, 58: PRINT "   ";
        PRINT USING "####"; year;
        LOCATE 25, 66: PRINT USING "###"; day; hr; min;
        IF ts < 60 THEN LOCATE 25, 75: PRINT USING "###"; sec;
       
        'Print Simulation data
121     IF targ = 40 THEN 123
        IF COS(VangleDIFF) <> 0 AND Dtarg - P(targ, 5) <> 0 THEN Acctarg = Acctarg + ((((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2) / (2 * (Dtarg - P(targ, 5)))) * COS(VangleDIFF))
123     oldAcctarg = Acctarg
        IF DISPflag = 1 THEN 113
        COLOR 12
        LOCATE 8, 16: IF CONSTacc = 1 THEN PRINT CHR$(67 + (10 * MATCHacc));  ELSE PRINT " ";
        COLOR 15
        'IF ref = 30 AND borrellyFLAG = 0 THEN Vref = 0
        LOCATE 2, 12
        IF Vref > 9999999 THEN PRINT USING "##.####^^^^"; Vref ELSE PRINT USING "########.##"; Vref;
        Vrefhab = SQR((Vx(28) - Vx(ref)) ^ 2 + (Vy(28) - Vy(ref)) ^ 2)
        LOCATE 3, 12
        IF Vrefhab > 9999999 THEN PRINT USING "##.####^^^^"; Vrefhab;  ELSE PRINT USING "########.##"; Vrefhab;
        Vreftarg = SQR((Vx(targ) - Vx(ref)) ^ 2 + (Vy(targ) - Vy(ref)) ^ 2)
        LOCATE 4, 12
        IF Vreftarg > 9999999 THEN PRINT USING "##.####^^^^"; Vreftarg;  ELSE PRINT USING "########.##"; Vreftarg;
        LOCATE 14, 7
        IF ABS(Acctarg) > 9999 THEN PRINT USING "##.##^^^^"; Acctarg;  ELSE PRINT USING "######.##"; Acctarg;
        LOCATE 13, 2
        IF Dtarg > 9.9E+11 THEN PRINT USING "##.########^^^^"; (Dtarg - P(targ, 5) - P(28, 5)) / 1000;  ELSE PRINT USING "###,###,###.###"; (Dtarg - P(targ, 5) - P(28, 5)) / 1000;
        LOCATE 15, 9: PRINT USING "####.##"; Atargref * RAD;
        IF Cdh = .005 THEN COLOR 14
        LOCATE 7, 8: IF Cdh < .001 THEN PRINT USING "#####.###"; Are;  ELSE PRINT USING "#####.##"; Are; : PRINT "P";
        COLOR 15
        LOCATE 8, 8: PRINT USING "#####.##"; Aacc;
        LOCATE 11, 6
        IF Dfuel = 0 THEN PRINT "H"; : PRINT USING "#########"; fuel; : PRINT CHR$(32 + (refuel * 11) + (ventfuel * 13));
        IF Dfuel = 1 THEN PRINT "A"; : PRINT USING "#########"; AYSEfuel; : PRINT CHR$(32 + (AYSErefuel * 11) + (AYSEventfuel * 13));
        IF Dfuel = 2 THEN PRINT "RCS"; : PRINT USING "#######"; vernP!;
        LOCATE 18, 9: PRINT USING "####.##"; DIFFangle;

        COLOR 15
124     GOSUB 3005
        GOSUB 3008
        GOSUB 3006
                               

113     'Timed back-up
        IF bkt - TIMER > 120 THEN bkt = TIMER
        IF bkt + 1 < TIMER THEN bkt = TIMER: GOSUB 800
        IF ufo2 = 1 THEN Px(39, 1) = Px(39, 1) - 1
        IF ufo2 = 1 AND Px(39, 1) < 1 THEN explCENTER = 39: GOSUB 6000
        OLDts = ts


        'Control input
103     z$ = INKEY$
        IF z$ = "" THEN 105
        IF z$ = "q" THEN GOSUB 900
        IF z$ = "`" THEN DISPflag = 1 - DISPflag: CLS : IF DISPflag = 0 THEN GOSUB 400
        IF z$ = CHR$(27) THEN GOSUB 910
        IF z$ = " " THEN cen = targ: cenXoff = Px(28, 3) - Px(cen, 3): cenYoff = Py(28, 3) - Py(cen, 3)
        IF z$ = CHR$(9) THEN Aflag = Aflag + 1: IF Aflag = 3 THEN Aflag = 0: GOSUB 400 ELSE GOSUB 400
        IF z$ = CHR$(0) + ";" THEN Sflag = 1: GOSUB 400
        IF z$ = CHR$(0) + "<" THEN Sflag = 0: GOSUB 400
        IF z$ = CHR$(0) + "=" THEN Sflag = 4: GOSUB 400
        IF z$ = CHR$(0) + ">" THEN Sflag = 2: GOSUB 400
        IF z$ = CHR$(0) + "?" THEN Sflag = 3: GOSUB 400
        IF z$ = "b" THEN Dfuel = Dfuel + 1: GOSUB 400
        IF z$ = CHR$(0) + "A" THEN Sflag = 5: GOSUB 400
        IF z$ = CHR$(0) + "B" THEN Sflag = 6: GOSUB 400
        IF z$ = CHR$(0) + "C" THEN OFFSET = -1 * (1 - ABS(OFFSET)): GOSUB 400
        IF z$ = CHR$(0) + "D" THEN OFFSET = 1 - ABS(OFFSET): GOSUB 400
        IF z$ = CHR$(0) + CHR$(134) THEN CONSTacc = 1 - CONSTacc: Accel = Aacc: MATCHacc = 0
        IF z$ = CHR$(0) + CHR$(133) THEN MATCHacc = 1 - MATCHacc: CONSTacc = MATCHacc
       
        IF z$ = "+" AND mag < 130000000000# THEN mag = mag / .75: CLS : GOSUB 400
        IF z$ = "-" AND mag > 6.8E-11 THEN mag = mag * .75: CLS : GOSUB 400
        IF z$ = CHR$(0) + "I" AND vernP! > 0 THEN HABrotate% = HABrotate% - 1: vernP! = vernP! - 1
        IF z$ = CHR$(0) + "G" AND vernP! > 0 THEN HABrotate% = HABrotate% + 1: vernP! = vernP! - 1
                                                                           

        IF z$ = "[" THEN GOSUB 460
        IF z$ = "]" THEN GOSUB 465
        IF z$ < "0" OR z$ > "U" THEN 110
        z = ASC(z$) - 48
        IF z = 36 AND MODULEflag = 0 THEN 110
        IF Aflag = 0 THEN cen = z: CLS : cenXoff = 0: cenYoff = 0: GOSUB 400
        IF z = 28 THEN 110
        IF Aflag = 1 THEN targ = z: GOSUB 400
        IF Aflag = 2 THEN ref = z: GOSUB 400
        
      
110     IF z$ = CHR$(0) + "S" THEN eng = eng + .1: GOSUB 400
        IF z$ = CHR$(0) + "R" THEN eng = eng - .1: GOSUB 400
        IF z$ = CHR$(0) + "Q" THEN eng = eng + 1: GOSUB 400
        IF z$ = CHR$(0) + "O" THEN eng = eng - 1: GOSUB 400
        IF z$ = "\" THEN eng = eng * -1: GOSUB 400
        IF z$ = CHR$(13) THEN eng = 100: GOSUB 400
        IF z$ = CHR$(8) THEN eng = 0: MATCHacc = 0: CONSTacc = 0: GOSUB 400
        IF z$ = CHR$(0) + "H" THEN vern = .1: vernA = 0
        IF z$ = CHR$(0) + "K" THEN vern = .1: vernA = 90
        IF z$ = CHR$(0) + "M" THEN vern = .1: vernA = -90
        IF z$ = CHR$(0) + "P" THEN vern = .1: vernA = 180
       
        IF z$ <> "v" THEN 107
        vflag = 1 - vflag
        LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (20 * SIN(Vvangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (20 * COS(Vvangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
        LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (30 * SIN(Atarg)) + (Px(28, 3) - cenX) * mag / AU, 220 + (30 * COS(Atarg)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
        LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (10 * SIN(Sangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (10 * COS(Sangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
107     IF z$ = "t" THEN trail = 1 - trail: CLS : GOSUB 400
        IF z$ = "l" THEN ORref = 1 - ORref: CLS : GOSUB 400
        IF z$ = CHR$(0) + "@" THEN Sflag = 7: angleOFFSET = (Atarg - Sangle): GOSUB 400
        IF z$ = "u" THEN tr = 1 - tr: CLS : GOSUB 400
        IF z$ = "d" THEN dte = dte + 1: LOCATE 25, 58: PRINT SPACE$(20); : GOSUB 400
        IF dte = 4 THEN dte = 0
        IF z$ = "p" THEN PROJflag = 1 - PROJflag: GOSUB 400
        IF z$ = "o" THEN GOSUB 3000
        IF z$ = "c" THEN CLS : GOSUB 400
        IF z$ = "z" THEN Ztel7 = 1 - SGN(Ztel)
        IF z$ = "x" THEN Ztel7 = 2 - (SGN(Ztel) * 2)
        'IF z$ = "w" THEN SRBtimer = 220
        IF Ztel(8) = 1 THEN 105
        IF z$ <> "/" THEN 104
        IF ts <= .5 THEN ts = ts - .125: GOSUB 400
        IF ts = 1 THEN ts = .5: GOSUB 400
        IF ts = 2 THEN ts = 1: GOSUB 400
        IF ts = 10 THEN ts = 2: GOSUB 400
        IF ts > 10 THEN ts = ts - 10: GOSUB 400
104     IF z$ <> "*" THEN 105
        IF ts > 9 THEN ts = ts + 10: GOSUB 400
        IF ts = 2 THEN ts = 10: GOSUB 400
        IF ts = 1 THEN ts = 2: GOSUB 400
        IF ts = .5 THEN ts = 1: GOSUB 400
        IF ts < .5 THEN ts = ts + .125: GOSUB 400
105     IF z$ = "s" THEN GOSUB 600
        IF z$ = "r" THEN GOSUB 700
        IF tttt - TIMER > ts * 10 THEN tttt = TIMER + (ts / 2)
        IF ts < .3 AND TIMER - tttt < ts THEN 103
        GOTO 100


        'SUBROUTINE Automatic space craft orientation calculations
301     IF explosion > 1 THEN Ztel(2) = 0: Ztel(1) = 1
        IF explosion1 > 1 AND AYSE = 150 THEN Ztel(2) = 0
        IF Ztel(1) = 1 THEN Sflag = 1: MATCHacc = 0: CONSTacc = 0
        IF SRBtimer > 0 THEN SRBtimer = SRBtimer - ts
        IF SRBtimer > 100 THEN SRB = 131250 ELSE SRB = 0
        IF vernP! < .01 THEN vernP! = 0

        COLOR 15
        Aoffset = ATN((P(targ, 5) * 1.01) / (Dtarg + .0001)): Atarg = Atarg - (Aoffset * OFFSET)
        difX = Vx(targ) - Vx(28)
        difY = Vy(targ) - Vy(28)
        GOSUB 5000
        Vvtangle = angle
        IF ORref = 1 THEN Aa = Atarg ELSE Aa = Aref
        IF PROJflag = 0 THEN DIFFangle = (Aa - Sangle) * RAD ELSE DIFFangle = (Atarg - Vvtangle) * RAD
        IF DIFFangle > 180 THEN DIFFangle = -360 + DIFFangle
        IF DIFFangle < -180 THEN DIFFangle = 360 + DIFFangle
       
        difX = Px(28, 3) - Px(Ztel(14), 3)
        difY = Py(28, 3) - Py(Ztel(14), 3)
        GOSUB 5000
        Wangle = angle
        VwindX = (Ztel(15) * SIN(Wangle + Ztel(16)))
        VwindY = (Ztel(15) * COS(Wangle + Ztel(16)))

        IF vernP! < .01 AND Sflag <> 1 THEN Sflag = 1: LOCATE 25, 11: PRINT "MAN      ";
        IF Sflag = 1 THEN Sangle = Sangle + (HABrotate% * .0086853 * ts): GOTO 302
        HABrotate% = 0
        vernP! = vernP! - .01
        IF Sflag = 2 THEN dSangle = Atarg ELSE dSangle = Aref
        IF Sflag = 7 THEN dSangle = Atarg
        dSangle = dSangle - (Aoffset * OFFSET)
        IF Sflag = 5 THEN dSangle = Vvtangle
        IF Sflag = 6 THEN dSangle = Vvtangle + 3.1415926535#
        IF Sflag = 0 THEN dSangle = dSangle - (90 / RAD)
        IF Sflag = 4 THEN dSangle = dSangle + (90 / RAD)
        IF Sflag = 3 THEN dSangle = dSangle - (180 / RAD)
        IF Sflag = 7 THEN dSangle = dSangle - angleOFFSET
        diffSangle = dSangle - Sangle
        IF diffSangle > pi THEN diffSangle = (-1 * pi2) + diffSangle
        IF diffSangle < (-1 * pi) THEN diffSangle = pi2 + diffSangle
        IF ABS(diffSangle) < .24 * ts THEN Sangle = dSangle: GOTO 302
        Sangle = Sangle + (.2 * ts * SGN(diffSangle))
       
302     IF Sangle < 0 THEN Sangle = Sangle + pi2
        IF Sangle > pi2 THEN Sangle = Sangle - pi2
        IF oldAcctarg < 0 THEN MATCHacc = 0
        IF DISPflag = 1 THEN 307
        LOCATE 5, 16: COLOR 15: PRINT USING "####.#"; eng;
        IF Sflag <> 1 THEN 307
        IF HABrotate% <> 0 THEN COLOR 15 ELSE COLOR 8
        LOCATE 25, 15: PRINT USING "##.#"; ABS(HABrotate%) / 2;
        COLOR 10
        LOCATE 25, 19: IF HABrotate% < 0 THEN PRINT ">";  ELSE PRINT " ";
        LOCATE 25, 14: IF HABrotate% > 0 THEN PRINT "<";  ELSE PRINT " ";
       
307     COLOR 15
        IF Ztel(2) = 0 THEN MATCHacc = 0: CONSTacc = 0
        IF MATCHacc = 1 THEN Accel = oldAcctarg
        HABmass = 275000 + fuel
        IF AYSE = 150 THEN HABmass = HABmass + 20000000 + AYSEfuel
        IF CONSTacc = 1 THEN Aacc = Accel: eng = Aacc * HABmass / Ztel(2) ELSE Aacc = (Ztel(2) * eng) / HABmass
        Av = (175000 * vern) / HABmass
        IF AYSE = 150 THEN Av = 0
        IF vernP! <= 0 THEN Av = 0
        IF Av > 0 THEN vernP! = vernP! - 1
        vern = 0

304     Aacc = Aacc + (SRB / HABmass) * 100
        P(i, 1) = P(i, 1) + (Aacc * SIN(Sangle))
        P(i, 2) = P(i, 2) + (Aacc * COS(Sangle))
        P(i, 1) = P(i, 1) + Av * SIN(Sangle + (vernA / RAD))
        P(i, 2) = P(i, 2) + Av * COS(Sangle + (vernA / RAD))
       

        THRUSTx = (Aacc * SIN(Sangle))
        THRUSTy = (Aacc * COS(Sangle))
        THRUSTx = THRUSTx + (Av * SIN(Sangle + (vernA / RAD)))
        THRUSTy = THRUSTy + (Av * COS(Sangle + (vernA / RAD)))
       
        Are = 0
        IF atm = 40 AND Ztel(16) <> 3.141593 THEN Are = 0: GOTO 319
        difX = Vx(atm) - Vx(28) + VwindX
        difY = Vy(atm) - Vy(28) + VwindY
        GOSUB 5000
        VvRangle = angle
        VVr = SQR((difX ^ 2) + (difY ^ 2))
        IF atm = 40 THEN Pr = .01: GOTO 320
        IF Ratm < 0 THEN Pr = P(atm, 8) ELSE Pr = P(atm, 8) * (2.71828 ^ (-1 * Ratm / P(atm, 9)))
320     Are = Pr * VVr * VVr * Cdh
        IF Are * ts > VVr / 2 THEN Are = (VVr / 2) / ts
        IF CONflag = 1 AND Ztel(16) = 0 THEN Are = 0
        P(i, 1) = P(i, 1) - (Are * SIN(VvRangle))
        P(i, 2) = P(i, 2) - (Are * COS(VvRangle))
        THRUSTx = THRUSTx - (Are * SIN(VvRangle))
        THRUSTy = THRUSTy - (Are * COS(VvRangle))
321     IF Pr > 100 AND Pr / 200 > RND THEN explFLAG1 = 1

319     Agrav = (THRUSTx - (Are * SIN(VvRangle))) ^ 2
        Agrav = Agrav + ((THRUSTy - (Are * COS(VvRangle))) ^ 2)
        Agrav = SQR(Agrav)
        IF CONflag = 1 THEN Agrav = CONacc
       
        IF THRUSTy = 0 THEN IF THRUSTy < 0 THEN THRUSTangle = .5 * 3.1415926535# ELSE THRUSTangle = 1.5 * 3.1415926535# ELSE THRUSTangle = ATN(THRUSTx / THRUSTy)
        IF THRUSTy > 0 THEN THRUSTangle = THRUSTangle + 3.1415926535#
        IF THRUSTx > 0 AND THRUSTy < 0 THEN THRUSTangle = THRUSTangle + 6.283185307#
      
        LOCATE 5, 8: COLOR 14
        IF SRB > 10 THEN PRINT "SRB";  ELSE PRINT "   ";
        IF AYSE = 150 THEN COLOR 10 ELSE COLOR 0
        LOCATE 5, 12: PRINT "AYSE";
        COLOR 7
       
        RETURN


       
        'SUBROUTINE print control variable names to screen
400     IF mag < .1 THEN GOSUB 8000
        IF ts < .125 THEN ts = .125
        IF ts > 60 THEN ts = 60
        IF Dfuel > 2 THEN Dfuel = 0
        IF ufo2 = 1 THEN ts = .25
        COLOR 8
        LOCATE 1, 1: PRINT CHR$(201); STRING$(9, 205); CHR$(209); STRING$(11, 205); CHR$(187);
        LOCATE 2, 1: PRINT CHR$(186); : LOCATE 2, 11: PRINT CHR$(179); : LOCATE 2, 23: PRINT CHR$(186);
        LOCATE 3, 1: PRINT CHR$(186); : LOCATE 3, 11: PRINT CHR$(179); : LOCATE 3, 23: PRINT CHR$(186);
        LOCATE 4, 1: PRINT CHR$(186); : LOCATE 4, 11: PRINT CHR$(179); : LOCATE 4, 23: PRINT CHR$(186);
        LOCATE 5, 1: PRINT CHR$(186); : LOCATE 5, 11: PRINT CHR$(179); : LOCATE 5, 23: PRINT CHR$(186);
        LOCATE 6, 1: PRINT CHR$(204); STRING$(9, 205); CHR$(207); STRING$(5, 205); CHR$(203); STRING$(5, 205); CHR$(188);
        COLOR 7
        IF Ztel(1) = 1 THEN Sflag = 1
        LOCATE 2, 2: PRINT "ref Vo";
        LOCATE 3, 2: PRINT "V hab-ref";
        LOCATE 4, 2: PRINT "Vtarg-ref";
        COLOR 7 '+ (5 * SGN(Ztel(2)))
        LOCATE 5, 2: PRINT "Engine"; : LOCATE 5, 16: COLOR 15: PRINT USING "####.#"; eng;
        COLOR 7 + (5 * Ztel(1))
        LOCATE 25, 2: PRINT "NAVmode";
        COLOR 14
        LOCATE 25, 10
        IF OFFSET = -1 THEN PRINT "-";
        IF OFFSET = 0 THEN PRINT " ";
        IF OFFSET = 1 THEN PRINT "+";
        COLOR 15
        LOCATE 25, 11
        IF Sflag = 0 THEN PRINT "ccw prog "; : GOTO 401
        IF Sflag = 4 THEN PRINT "ccw retro"; : GOTO 401
        IF Sflag = 1 THEN PRINT "MAN      "; : GOTO 401
        IF Sflag = 2 THEN PRINT "app targ "; : GOTO 401
        IF Sflag = 5 THEN PRINT "pro Vtrg "; : GOTO 401
        IF Sflag = 6 THEN PRINT "retr Vtrg"; : GOTO 401
        IF Sflag = 7 THEN PRINT "hold Atrg"; : GOTO 401
        IF Sflag = 3 THEN PRINT "deprt ref";
401     COLOR 8
        LOCATE 21, 1: PRINT CHR$(204); STRING$(7, 205); CHR$(209); STRING$(7, 205); CHR$(202); CHR$(205); CHR$(205); CHR$(187);
        LOCATE 22, 1: PRINT CHR$(186); : LOCATE 22, 9: PRINT CHR$(179); : LOCATE 22, 20: PRINT CHR$(186);
        LOCATE 23, 1: PRINT CHR$(186); : LOCATE 23, 9: PRINT CHR$(179); : LOCATE 23, 20: PRINT CHR$(186);
        LOCATE 24, 1: PRINT CHR$(186); : LOCATE 24, 9: PRINT CHR$(179); : LOCATE 24, 20: PRINT CHR$(186);
        LOCATE 25, 1: PRINT CHR$(186); : LOCATE 25, 9: PRINT CHR$(179); : LOCATE 25, 20: PRINT CHR$(186);
        LOCATE 26, 1: PRINT CHR$(200); STRING$(7, 205); CHR$(207); STRING$(10, 205); CHR$(188);
        LOCATE 10, 1: PRINT CHR$(204); STRING$(15, 205); CHR$(185);
        LOCATE 11, 1: PRINT CHR$(186); : LOCATE 11, 17: PRINT CHR$(186);
        LOCATE 12, 1: PRINT CHR$(199); STRING$(15, 196); CHR$(182);
        LOCATE 13, 1: PRINT CHR$(186); : LOCATE 13, 17: PRINT CHR$(186);
        LOCATE 14, 1: PRINT CHR$(186); : LOCATE 14, 17: PRINT CHR$(186);
        LOCATE 15, 1: PRINT CHR$(186); : LOCATE 15, 17: PRINT CHR$(186);
        LOCATE 16, 1: PRINT CHR$(186); : LOCATE 16, 17: PRINT CHR$(186);
        LOCATE 17, 1: PRINT CHR$(186); : LOCATE 17, 17: PRINT CHR$(186);
        LOCATE 18, 1: PRINT CHR$(186); : LOCATE 18, 17: PRINT CHR$(186);
        LOCATE 19, 1: PRINT CHR$(186); : LOCATE 19, 17: PRINT CHR$(186);
        LOCATE 20, 1: PRINT CHR$(186); : LOCATE 20, 17: PRINT CHR$(186);
        LOCATE 7, 1: PRINT CHR$(186); : LOCATE 7, 17: PRINT CHR$(186);
        LOCATE 8, 1: PRINT CHR$(186); : LOCATE 8, 17: PRINT CHR$(186);
        LOCATE 9, 1: PRINT CHR$(186); : LOCATE 9, 17: PRINT CHR$(186);
        IF dte > 0 THEN LOCATE 24, 57: PRINT CHR$(201); STRING$(20, 205); CHR$(187);
        IF dte > 0 THEN LOCATE 25, 57: PRINT CHR$(186); : LOCATE 25, 78: PRINT CHR$(186);
        IF dte > 0 THEN LOCATE 26, 57: PRINT CHR$(200); STRING$(20, 205); CHR$(188);
        IF Aflag = 0 THEN COLOR 10 ELSE COLOR 7
        LOCATE 22, 2: PRINT "center "; : COLOR 15: LOCATE 22, 11: PRINT Znme$(cen);
        IF Aflag = 1 THEN COLOR 10 ELSE COLOR 7
        LOCATE 23, 2: PRINT "target "; : COLOR 15: LOCATE 23, 11: PRINT Znme$(targ);
        IF Aflag = 2 THEN COLOR 10 ELSE COLOR 7
        LOCATE 24, 2: PRINT "ref    "; : COLOR 15: LOCATE 24, 11: PRINT Znme$(ref);
        COLOR 15
        LOCATE 9, 11: PRINT USING "##.###"; ts;
        COLOR 7
        LOCATE 11, 2: PRINT "Fuel";
        LOCATE 14, 2: PRINT "Acc";
        LOCATE 15, 2: PRINT CHR$(233); " Hrt";
        LOCATE 16, 2: PRINT "Vcen          "; : IF ORref = 0 THEN PRINT "R";
        LOCATE 17, 2: PRINT "Vtan          "; : IF ORref = 0 THEN PRINT "R";
        LOCATE 18, 2: PRINT CHR$(233); Znme$(41 + PROJflag); "         ";
        IF PROJflag = 0 AND ORref = 0 THEN PRINT "R";  ELSE PRINT " ";
        LOCATE 19, 2: PRINT "Peri          "; : IF ORref = 0 THEN PRINT "R";
        LOCATE 20, 2: PRINT "Apo           "; : IF ORref = 0 THEN PRINT "R";
        COLOR 15
402     'IF dte = 1 THEN LOCATE 25, 60: PRINT USING "####"; year; : LOCATE 25, 66: PRINT USING "###"; day; hr; min; sec;
        RETURN



460     ON Aflag + 1 GOTO 461, 462, 463
461     IF cen = 40 THEN cen = 38
        IF cen - 1 = 36 AND MODULEflag = 0 THEN cen = 36
        IF cen - 1 < 0 THEN cen = 41
        cen = cen - 1
        CLS
        cenXoff = 0
        cenYoff = 0
        GOTO 464

462     IF targ - 1 = 28 THEN targ = 28
        IF targ - 1 = 36 AND MODULEflag = 0 THEN targ = 36
        IF targ - 1 < 0 THEN targ = 41
        IF targ = 40 THEN targ = 38 + ufo1 + ufo2
        targ = targ - 1
        GOTO 464

463     IF ref - 1 = 28 THEN ref = 28
        IF ref - 1 = 36 AND MODULEflag = 0 THEN ref = 36
        IF ref - 1 < 0 THEN ref = 35
        ref = ref - 1
       
        
464     GOSUB 400
        RETURN


465     ON Aflag + 1 GOTO 466, 467, 468
466     IF cen = 40 THEN cen = -1
        IF cen + 1 = 36 AND MODULEflag = 0 THEN cen = 36
        IF cen + 1 > 37 THEN cen = 39
        cen = cen + 1
        CLS
        cenXoff = 0
        cenYoff = 0
        GOTO 469

467     IF targ = 40 THEN targ = -1
        IF targ + 1 = 28 THEN targ = 28
        IF targ + 1 = 36 AND MODULEflag = 0 THEN targ = 36
        IF targ + 1 > 37 + ufo1 + ufo2 THEN targ = 39
        targ = targ + 1
        GOTO 469

468     IF ref + 1 = 28 THEN ref = 28
        IF ref + 1 = 35 THEN ref = -1
        IF ref + 1 > 37 THEN ref = 36
        ref = ref + 1
       
469     GOSUB 400
        RETURN


        'SUBROUTINE Restore data from file
700     LOCATE 10, 60: PRINT "Load File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN 703
704     OPEN "R", #1, filename$
        IF LOF(1) > 1 THEN 701
        CLOSE #1
        LOCATE 11, 60: PRINT filename$; " is empty";
702     LOCATE 10, 60: PRINT "                  ";
        GOTO 700
701     CLOSE #1
        OPEN "I", #1, filename$
        INPUT #1, z$
        IF z$ <> "ORBIT5S" THEN LOCATE 11, 60: PRINT filename$; " is unusable"; : CLOSE #1: GOTO 702
        INPUT #1, eng, vflag, Aflag, Sflag, zz
        INPUT #1, mag, Sangle, cen, targ, ref
        INPUT #1, trail, tr, dte, ts, Eflag
        INPUT #1, year, day, hr, min, sec
        INPUT #1, AYSEangle, AYSEscrape, zz, zz, HABrotate%, AYSE
        INPUT #1, zz, MODULEflag, AYSEdist, OCESSdist, explosion, explosion1
        INPUT #1, Px(0, 3), Py(0, 3), Vx(0), Vy(0), P(0, 1), P(0, 2)
        trail = 1 AND trail
        OLDts = INT(ts / 100)
        ts = ts - (OLDts * 100)
        OLDts = OLDts / 1000
        IF OLDts = 0 THEN OLDts = ts
        Px(0, 3) = 0
        Py(0, 3) = 0
        P(0, 1) = 0
        FOR i = 1 TO 37
         INPUT #1, Px(i, 3), Py(i, 3), Vx(i), Vy(i), P(i, 1), P(i, 2)
        NEXT i
        FOR i = 1 TO 12
         INPUT #1, z1
        NEXT i
        INPUT #1, fuel, AYSEfuel
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        Px(38, 3) = 0: Py(38, 3) = 0: Vx(38) = 0: Vy(38) = 0: P(38, 1) = 0: P(38, 2) = 0
        Px(39, 3) = 0: Py(39, 3) = 0: Vx(39) = 0: Vy(39) = 0: P(39, 1) = 0: P(39, 2) = 0
        tttt = TIMER + ts
        ufo1 = 0
        ufo2 = 0
        cenXoff = 0
        cenYoff = 0
        cenX = Px(cen, 3)
        cenY = Py(cen, 3)
703     CLS
        CLOSE #1
        explosion = 0
        explosion1 = 0
        GOSUB 400
        RETURN



        'SUBROUTINE save data to file
600     LOCATE 9, 60: PRINT "8 charaters a-z 0-9";
        LOCATE 10, 60: PRINT "Save File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN CLS : GOSUB 400: RETURN
        OPEN "R", #1, filename$
        IF LOF(1) < 1 THEN 601
        LOCATE 11, 60: PRINT "File exists";
        LOCATE 12, 60: PRINT "overwrite? "; : INPUT ; "", z$
        IF UCASE$(LEFT$(z$, 1)) = "Y" THEN 601
        FOR i = 9 TO 12
         LOCATE i, 60: PRINT "                  ";
        NEXT i
        CLOSE #1
        GOTO 600
601     CLOSE #1
        OPEN "O", #1, filename$
620     CLS
        GOSUB 400
        Eflag = Eflag + 1
        GOTO 801
       

        'SUBROUTINE Timed back-up
800     OPEN "O", #1, "OSbackup"
801     PRINT #1, "ORBIT5S"
        Zx = trail
        IF Cdh = .005 THEN Zx = Zx + 2
        IF SRB > 0 THEN Zx = Zx + 4
        PRINT #1, eng; ","; vflag; ","; Aflag; ","; Sflag; ","; Are
        PRINT #1, mag; ","; Sangle; ","; cen; ","; targ; ","; ref
        PRINT #1, Zx; ","; tr; ","; dte; ","; ts + (100000 * OLDts); ","; Eflag
        PRINT #1, year; ","; day; ","; hr; ","; min; ","; sec
        PRINT #1, AYSEangle; ","; AYSEscrape; ","; Ztel(15); ","; Ztel(16); ","; HABrotate%; ","; AYSE
        PRINT #1, Ztel(9); ","; MODULEflag; ","; AYSEdist; ","; OCESSdist; ","; explosion; ","; explosion1
        PRINT #1, Ztel(1); ","; Ztel(2); ","; Ztel(14); ","; LONGtarg; ","; Pr; ","; Agrav
        FOR i = 1 TO 39
         PRINT #1, Px(i, 3); ","; Py(i, 3); ","; Vx(i); ","; Vy(i); ","; P(i, 1); ",";
         IF i = 1 THEN PRINT #1, vernP! ELSE PRINT #1, P(i, 2)
        NEXT i
        PRINT #1, fuel; ","; AYSEfuel
        CLOSE #1

813     OPEN "I", #1, "MST.dat"
        INPUT #1, MST#
        INPUT #1, EST#
        INPUT #1, LONGtarg: LONGtarg = (LONGtarg + 180) / RAD
        CLOSE #1
        Ltx = (P(ref, 5) * SIN(LONGtarg))
        Lty = (P(ref, 5) * COS(LONGtarg))
        Ltr = ref

811     OPEN "I", #1, "ORBITSse"
        FOR i = 1 TO 23
         IF EOF(1) THEN CLOSE #1: GOTO 812
         INPUT #1, Ztel(i)
        NEXT i
        CLOSE #1
         'Ztel(1) = nav mode enable
        IF Ztel(1) > 5 THEN RUN "orbit5t"
        'Ztel(2) = engine force factor
        fuel = Ztel(3)  'HAB fuel mass
        AYSEfuel = Ztel(4)  'AYSE fuel mass
        'Ztel(5) = HAB explosion
        'Ztel(6) = AYSE explosion
        'Ztel(7) = Ztel7: Ztel7 = 0
        IF Ztel(7) = 2 AND MODULEflag = 0 THEN GOSUB 3200
        IF Ztel(7) = 1 AND MODULEflag > 0 THEN GOSUB 3200
        IF Ztel(8) = 1 THEN ts = .125
        'Ztel(9) = rshield
        Zx = 1 AND Ztel(10)
        IF Zx = 1 AND vernP! < 100 THEN vernP! = vernP! + 25 * ts
        IF vernP! > 120 THEN vernP! = 120
        IF vernP! < 0 THEN vernP! = 0
        Zx = 2 AND Ztel(10)
        IF Zx = 2 THEN Cdh = .005 ELSE Cdh = .0002
        Zx = 4 AND Ztel(10)
        IF Zx = 4 AND SRBtimer < 1 THEN SRBtimer = 220
        Zx = 8 AND Ztel(10)
        IF Zx = 8 THEN explosion = 2
        Zx = 16 AND Ztel(10)
        IF Zx = 16 THEN explosion1 = 2
        AYSE = Ztel(13)
        IF explosion > 0 THEN explosion = explosion - 1
        IF explosion1 > 0 THEN explosion1 = explosion1 - 1
        IF Ztel(1) = 1 THEN Sflag = 1
        IF DISPflag = 0 THEN COLOR 7 + (5 * Ztel(1)): LOCATE 25, 2: PRINT "NAVmode";
        COLOR 15
        IF ufoTIMER > 0 THEN ufoTIMER = ufoTIMER - 1: GOTO 812
        IF Ztel(17) = 1 AND ufo1 = 0 THEN GOSUB 7000
        IF Ztel(17) = 2 THEN ufo1 = 0: Px(38, 3) = 0: Py(38, 3) = 0: ufo2 = 0: Px(39, 3) = 0: Py(39, 3) = 0
        IF Ztel(23) >= 0 THEN 815
         ufoTIMER = 10
         ufo1 = 0
         ufo2 = 0
         Zt = ABS(Ztel(23))
         Px(Zt, 3) = Px(38, 3)
         Py(Zt, 3) = Py(38, 3)
         Vx(Zt) = Vx(38)
         Vy(Zt) = Vy(38)
         P(Zt, 1) = P(38, 1)
         P(Zt, 2) = P(38, 2)
         Px(38, 3) = 0
         Py(38, 3) = 0
         Px(39, 3) = 0
         Py(39, 3) = 0
         CONflag2 = 0
         GOTO 812
815     IF Ztel(23) < 38 AND ufo2 = 0 AND ufo1 = 1 THEN GOSUB 7100
        IF Ztel(23) = 39 AND ufo2 = 1 THEN explCENTER = 39: GOSUB 6000
812     COLOR 15
        RETURN


        'Confirm end program
900     LOCATE 10, 60: INPUT ; "End Program "; z$
        IF UCASE$(z$) = "Y" THEN END
        LOCATE 10, 60: PRINT "                   ";
        RETURN

        'Name and author
910     LOCATE 2, 60: PRINT "OCESS Orbit 5 T  ";
        LOCATE 3, 60: PRINT CHR$(74); CHR$(97); CHR$(109); CHR$(101); CHR$(115); " "; CHR$(77); CHR$(97); CHR$(103); CHR$(119); CHR$(111); CHR$(111); CHR$(100);
        RETURN

        'Orbit Projection
3000    GOSUB 3005
        GOSUB 3008
        GOSUB 3006
        L# = 2 * orbA
        IF ecc < 1 THEN L# = (1 - (ecc ^ 2)) * orbA
        IF ecc > 1 THEN L# = ((ecc ^ 2) - 1) * orbA
        difX = Px(ORrefOBJ, 3) - Px(28, 3)
        difY = Py(ORrefOBJ, 3) - Py(28, 3)
        GOSUB 5000
        r# = SQR((difX ^ 2) + (difY ^ 2))
        term# = (L# / r#) - 1
        IF ABS(ecc) < .0000001# THEN ecc = SGN(ecc) * .0000001#
        term# = term# / ecc
        IF ABS(term#) > 1 THEN num# = 0 ELSE num# = eccFLAG * SQR(1 - (term# ^ 2))
        dem# = 1 - term#
        difA# = 2 * ATN(num# / dem#)
        difA# = 3.1415926# - difA# - angle#
        stp = .1
        lim1 = -180: lim2 = 180
        IF ecc < 1 THEN lim1 = 0: lim2 = 179
        IF ecc > 1 THEN GOSUB 3010
        FRAMEflag = 0
3003    FOR i = lim1 TO lim2 STEP stp
         angle# = i / 57.29578
         d# = 1 + (ecc * COS(angle#))
         r# = L# / d#
         difX# = (r# * SIN(angle# - difA#)) + Px(ORrefOBJ, 3)
         difY# = (r# * COS(angle# - difA#)) + Py(ORrefOBJ, 3)
         IF ecc < 1 THEN 3018
         IF ABS(i - lim1) < stp THEN difX1 = difX#: difY1 = difY#
         IF ABS(i - lim2) < stp THEN difX2 = difX#: difY2 = difY#
         IF ABS(i - 0) < stp THEN difX3 = difX#: difY3 = difY#
         GOTO 3019
3018     IF ABS(i - 180) < stp THEN difX1 = difX#: difY1 = difY#
         IF ABS(i - lim2) < stp THEN difX3 = difX#: difY3 = difY#
3019     difX# = 300 + ((difX# - cenX) * mag / AU)
         difY# = 220 + ((difY# - cenY) * mag / AU)
         IF ABS(300 - difX#) > 400 OR ABS(220 - difY#) > 300 THEN FRAMEflag = 0: GOTO 3002
         IF FRAMEflag = 0 THEN PSET (difX#, difY#), 15 ELSE LINE -(difX#, difY#), 15
         PSET (difX#, difY#), 15
         FRAMEflag = 1
3002    NEXT i
        IF ecc < 1 AND lim2 = 179 THEN lim1 = 179: lim2 = 181: stp = .001: GOTO 3003
        IF ecc < 1 AND lim2 = 181 THEN lim1 = 181: lim2 = 359.9: stp = .1: GOTO 3003
        GOSUB 3020
        RETURN
       
3005    IF ORref = 1 THEN ORrefD = Dtarg: ORrefOBJ = targ: GOTO 3009
        difX = Vx(ref) - Vx(28)
        difY = Vy(ref) - Vy(28)
        GOSUB 5000
        ORrefOBJ = ref
        VangleDIFF = Aref - angle
        ORrefD = Dref
3009    RETURN

3006    orbEk# = (((Vx(28) - Vx(ORrefOBJ)) ^ 2 + (Vy(28) - Vy(ORrefOBJ)) ^ 2)) / 2
        orbEp# = -1 * G * P(ORrefOBJ, 4) / ORrefD
        orbD# = G * P(ORrefOBJ, 4)
        IF orbD# = 0 THEN orbD# = G * 1
        L2# = (ORrefD * Vtan) ^ 2
        orbE# = orbEk# + orbEp#
        term2# = 2 * orbE# * L2# / (orbD# * orbD#)
        ecc = SQR(1 + term2#)
        orbA = orbD# / ABS(2 * orbE#)
        PROJmax = orbA * (1 + ecc)
        PROJmin = orbA * (1 - ecc)
        IF ecc = 1 THEN PROJmin = orbA
        IF ecc > 1 THEN PROJmin = orbA * (ecc - 1)
        IF DISPflag = 1 THEN RETURN
        LOCATE 19, 7
        IF ABS(PROJmin) > 89999999 THEN PRINT USING "##.##^^^^"; PROJmin / 1000;  ELSE PRINT USING "######.##"; (PROJmin - P(ORrefOBJ, 5)) / 1000;
        LOCATE 20, 7
        IF ecc >= 1 THEN PRINT "  -------"; : GOTO 3007
        IF ABS(PROJmax) > 89999999 THEN PRINT USING "##.##^^^^"; PROJmax / 1000;  ELSE PRINT USING "######.##"; (PROJmax - P(ORrefOBJ, 5)) / 1000;
3007    RETURN

3008    Vcen = SQR(((Vx(28) - Vx(ORrefOBJ)) ^ 2 + (Vy(28) - Vy(ORrefOBJ)) ^ 2)) * -1 * COS(VangleDIFF)
        Vtan = SQR(((Vx(28) - Vx(ORrefOBJ)) ^ 2 + (Vy(28) - Vy(ORrefOBJ)) ^ 2)) * (SIN(VangleDIFF))
        IF DISPflag = 1 THEN RETURN
        LOCATE 16, 7
        IF ABS(Vcen) > 99999 THEN PRINT USING "##.##^^^^"; Vcen;  ELSE PRINT USING "######.##"; Vcen;
        LOCATE 17, 7
        IF ABS(Vtan) > 99999 THEN PRINT USING "##.##^^^^"; Vtan;  ELSE PRINT USING "######.##"; Vtan;
        eccFLAG = SGN(Vcen) * SGN(Vtan)
        IF Vcen = 0 THEN eccFLAG = SGN(Vtan)
        IF Vtan = 0 THEN eccFLAG = SGN(Vcen)
        RETURN

3010    term# = 1 / ecc
        dem# = 1 + SQR(1 - (term# ^ 2))
        term# = term# / dem#
        term# = (2 * ATN(term#) * 57.29578) + 90
        lim1 = -1 * term#
        lim2 = term#
        RETURN

3020    IF targ = ref THEN RETURN
        difX = difX1 - Px(ref, 3)
        difY = difY1 - Py(ref, 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        AtoAPOAPSIS = ABS(angle - Atr)
        IF AtoAPOAPSIS > 3.1415926535# THEN AtoAPOAPSIS = 6.283185307# - AtoAPOAPSIS
        LOCATE 27, 2
        PRINT CHR$(233); " tRa";
        LOCATE 27, 10
        PRINT USING "###"; AtoAPOAPSIS * RAD; : PRINT CHR$(248);
        IF ecc < 1 THEN 3021
        difX = difX2 - Px(ref, 3)
        difY = difY2 - Py(ref, 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        AtoAPOAPSIS = ABS(angle - Atr)
        IF AtoAPOAPSIS > 3.1415926535# THEN AtoAPOAPSIS = 6.283185307# - AtoAPOAPSIS
        PRINT USING "#####"; AtoAPOAPSIS * RAD; : PRINT CHR$(248);
3021    difX = difX3 - Px(ref, 3)
        difY = difY3 - Py(ref, 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        AtoAPOAPSIS = ABS(angle - Atr)
        IF AtoAPOAPSIS > 3.1415926535# THEN AtoAPOAPSIS = 6.283185307# - AtoAPOAPSIS
        LOCATE 28, 2
        PRINT CHR$(233); " tRp";
        LOCATE 28, 10
        PRINT USING "###"; AtoAPOAPSIS * RAD; : PRINT CHR$(248);
        RETURN
        '****************************************************

        'Restore orbital altitude of ISS after large time step
3100    difX = Px(3, 3) - Px(35, 3)
        difY = Py(3, 3) - Py(35, 3)
        GOSUB 5000
        Px(35, 3) = Px(3, 3) + ((P(3, 5) + 365000) * SIN(angle))
        Py(35, 3) = Py(3, 3) + ((P(3, 5) + 365000) * COS(angle))
        Vx(35) = Vx(3) + (SIN(angle + 1.570796) * SQR(G * P(3, 4) / (P(3, 5) + 365000)))
        Vy(35) = Vy(3) + (COS(angle + 1.570796) * SQR(G * P(3, 4) / (P(3, 5) + 365000)))
        RETURN

3200    'LOCATE 23, 40: PRINT CONflag;
        IF CONflag = 0 THEN 3299
        IF MODULEflag = 0 THEN 3210
        difX = Px(28, 3) - Px(36, 3)
        difY = Py(28, 3) - Py(36, 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        IF r > 90 THEN 3299
        IF targ = 36 THEN targ = CONtarg
        IF ref = 36 THEN ref = CONtarg
        IF cen = 36 THEN cen = 28
        MODULEflag = 0
        CLS
        GOSUB 400
        GOTO 3299

3210    Px(36, 3) = Px(28, 3) - ((80 - P(36, 5)) * SIN(Sangle))
        Py(36, 3) = Py(28, 3) - ((80 - P(36, 5)) * COS(Sangle))
        P(36, 1) = Px(36, 3) - Px(CONtarg, 3)
        P(36, 2) = Py(36, 3) - Py(CONtarg, 3)
        MODULEflag = CONtarg
        Vx(36) = Vx(MODULEflag)
        Vy(36) = Vy(MODULEflag)

3299    RETURN



5000    IF difY = 0 THEN IF difX < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difX / difY)
        IF difY > 0 THEN angle = angle + 3.1415926535#
        IF difX > 0 AND difY < 0 THEN angle = angle + 6.283185307#
        RETURN


        'Explosions
6000    Xexpl = 300 + (Px(explCENTER, 3) - cenX) * mag / AU
        Yexpl = 220 + (Py(explCENTER, 3) - cenY) * mag / AU
        PLAY "ML L25 GD MB"
        IF ABS(Xexpl) > 1000 OR ABS(Yexpl) > 1000 THEN 6001
        FOR Xj = 0 TO 14
         FOR Xi = 1 TO (49 - (2 * Xj))
          explANGLE = RND * 2 * 3.1415926535#
          Xexpl1 = Xexpl + (SIN(explANGLE) * Xj * 2)
          Yexpl1 = Yexpl + (COS(explANGLE) * Xj * 2)
          n = INT(RND * 5)
          IF n = 0 THEN cl = 6
          IF n = 1 THEN cl = 12
          IF n = 2 THEN cl = 7
          IF n = 3 THEN cl = 14
          IF n = 4 THEN cl = 15
          PRESET (Xexpl1, Yexpl1), cl
         NEXT Xi
         FOR Xi = 1 TO 100000: NEXT Xi
        NEXT Xj
        FOR Xj = 1 TO 56
         CIRCLE (Xexpl, Yexpl), Xj / 2, 0
         LINE (Xexpl - Xj / 3, Yexpl - Xj / 3)-(Xexpl + Xj / 3, Yexpl + Xj / 3), 0, BF
        NEXT Xj
6001    LOCATE 1, 35
        IF i < 0 THEN i = 0
        IF i > 39 THEN i = 0
        IF explCENTER = 39 THEN ufo2 = 0: Px(39, 3) = 0: Py(39, 3) = 0
        IF explCENTER = 39 AND B(i, 0) <> 28 THEN ufo1 = 0: Px(38, 3) = 0: Py(38, 3) = 0
        IF explCENTER = 39 AND B(i, 0) = 28 THEN CONflag = 1: CONtarg = B(0, i): Dcon = r: Acon = angle: CONacc = a
        IF explCENTER = 38 AND B(i, 0) = 28 THEN CONflag = 1: CONtarg = B(0, i): Dcon = r: Acon = angle: CONacc = a
        IF explCENTER = 38 THEN ufo1 = 0: Px(38, 3) = 0: Py(38, 3) = 0
        IF explCENTER = 28 OR explCENTER = 32 THEN ts = .25
        IF explCENTER = 28 THEN explosion = 12: Ztel(2) = 0: Ztel(1) = 0: LOCATE 25, 2: PRINT "NAVmode"; : LOCATE 25, 11: PRINT "manual   ";
        IF explCENTER = 32 THEN explosion1 = 12
        COLOR 15
        LOCATE 8, 10: PRINT USING "##.###"; ts;
        RETURN



7000    r = Ztel(19) + P(Ztel(18), 5)
        a = G * P(Ztel(18), 4) / (r ^ 2)
        angle = Ztel(20)
        V = SQR(G * P(Ztel(18), 4) / r)
        ZDangle = 0
        IF Ztel(21) = 1 THEN ZDangle = -90
        IF Ztel(21) = 0 THEN ZDangle = 90
        IF Ztel(21) = 2 THEN ZDangle = 180
        Vx(38) = V * SIN(angle + (ZDangle / RAD))
        Vy(38) = V * COS(angle + (ZDangle / RAD))
        Vx(38) = Vx(38) + Vx(Ztel(18))
        Vy(38) = Vy(38) + Vy(Ztel(18))
        Px(38, 3) = Px(Ztel(18), 3) + (r * SIN(angle))
        Py(38, 3) = Py(Ztel(18), 3) + (r * COS(angle))
        ufo1 = 1
        z$ = ""
        RETURN

7100    Px(39, 3) = Px(38, 3)
        Py(39, 3) = Py(38, 3)
        difX = Px(39, 3) - Px(Ztel(23), 3)
        difY = Py(39, 3) - Py(Ztel(23), 3)
        r = SQR((difY ^ 2) + (difX ^ 2))
        GOSUB 5000
        Vt = r / 10000
        IF Vt > 1000 THEN 7110
        Vt = CINT(Vt)
        V = r / Vt
        Vx(39) = Vx(Ztel(23)) + (V * SIN(angle))
        Vy(39) = Vy(Ztel(23)) + (V * COS(angle))
        ufo2 = 1
        Px(39, 1) = 4000
7110    RETURN


7200    difX = Px(38, 3) - Px(Ztel(18), 3)
        difY = Py(38, 3) - Py(Ztel(18), 3)
        GOSUB 5000
        IF Ztel(21) = 0 THEN angle = angle - (90 / RAD)
        IF Ztel(21) = 1 THEN angle = angle + (90 / RAD)
        IF Ztel(21) = 2 THEN angle = angle + (180 / RAD)
        Vx(38) = Vx(38) + (Ztel(22) * ts * SIN(angle))
        Vy(38) = Vy(38) + (Ztel(22) * ts * COS(angle))
        RETURN

8000    FOR i = 1 TO 3021
         IF ABS(300 + (Pz(i, 1) - cenX) * mag / AU) > 1000 THEN 8001
         IF ABS(220 + (Pz(i, 2) - cenY) * mag / AU) > 1000 THEN 8001
         PSET (300 + (Pz(i, 1) - cenX) * mag / AU, 220 + (Pz(i, 2) - cenY) * mag * 1 / AU), Pz(i, 0)
8001    NEXT i
        RETURN


8100    time# = (year * 31536000#) + (day * 86400#) + (hr * 3600#) + (min * 60#) + sec
        IF dte = 2 THEN etime# = MST# ELSE etime# = EST#
        IF time# > etime# THEN dtime# = time# - etime#: TIMEsgn = 1 ELSE dtime# = etime# - time#: TIMEsgn = -1

        IF TIMEsgn = -1 AND dtime# < 121 THEN ts = .125
        dyr# = INT(dtime# / 31536000#)
        dday# = dtime# - (dyr# * 31536000#)
        dday# = INT(dday# / 86400#)
        dhr# = dtime# - (dyr# * 31536000#) - (dday# * 86400#)
        dhr# = INT(dhr# / 3600#)
        dmin# = dtime# - (dyr# * 31536000#) - (dday# * 86400#) - (dhr# * 3600#)
        dmin# = INT(dmin# / 60#)
        dsec# = dtime# - (dyr# * 31536000#) - (dday# * 86400#) - (dhr# * 3600#) - (dmin# * 60#)
        LOCATE 25, 58
        IF dte = 2 THEN PRINT "M:";  ELSE PRINT "E:";
        IF TIMEsgn = -1 THEN PRINT "-";  ELSE PRINT " ";
        LOCATE 25, 61: PRINT USING "####"; dyr#; : LOCATE 25, 66: PRINT USING "###"; dday#; dhr#; dmin#;
        IF ts < 60 THEN LOCATE 25, 75: PRINT USING "###"; dsec#;

        RETURN


9000    LOCATE 1, 30
        IF ERL = 800 THEN CLOSE #1: RESUME 811
        IF ERL = 813 THEN CLOSE #1: RESUME 811
        IF ERL = 811 THEN CLOSE #1: RESUME 812
        IF ERL = 91 THEN CLOSE #1: CLS : PRINT "'stars' file is missing or incomplete"
        IF ERL = 80 THEN CLOSE #1: RESUME 51
        PRINT ERR, ERL
        z$ = INPUT$(1)
        END


9111    mmag = mag
        FOR mmagK = 1 TO 100
        FOR i = 37 + ufo1 + ufo2 TO 0 STEP -1
         IF i = 36 AND MODULEflag = 0 THEN 9109
         IF SQR(((Px(i, 3) - cenX) * mmag / AU) ^ 2 + ((Py(i, 3) - cenY) * mmag * 1 / AU) ^ 2) - (P(i, 5) * mmag / AU) > 400 THEN 9109
         IF mmag * P(i, 5) / AU > 3200 THEN 9119
         IF i = 28 THEN pld = 2 * ABS(SGN(eng))
         IF mmag * P(i, 5) / AU < 1.1 THEN PSET (300 + (Px(i, 3) - cenX) * mmag / AU, 220 + (Py(i, 3) - cenY) * mmag * 1 / AU), P(i, 0) + pld: GOTO 9109
         CIRCLE (300 + (Px(i, 3) - cenX) * mmag / AU, 220 + (Py(i, 3) - cenY) * mmag * 1 / AU), mmag * P(i, 5) / AU, P(i, 0) + pld
9119
9109     NEXT i
         FOR i = 1 TO 3021
         IF ABS(300 + (Pz(i, 1) - cenX) * mmag / AU) > 1000 THEN 9801
         IF ABS(220 + (Pz(i, 2) - cenY) * mmag / AU) > 1000 THEN 9801
         PSET (300 + (Pz(i, 1) - cenX) * mmag / AU, 220 + (Pz(i, 2) - cenY) * mmag * 1 / AU), Pz(i, 0)
9801     NEXT i
         
         IF mmag < .1 THEN GOSUB 8000
         mmag = mmag / (1.5)
         mgT = TIMER
9811     IF TIMER - mgT < .05 THEN 9811
         IF mmag < 8E-11 THEN 9911
        NEXT mmagK
9911    RUN "orbit6t.exe"

