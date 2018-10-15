1111    ON ERROR GOTO 9000
        'CLEAR , , 1024
        SCREEN 12
        PALETTE 8, 19 + (19 * 256) + (19 * 65536)
        DEFDBL A-Z
        DIM P(40, 11), Px(40, 5), Py(40, 5), Vx(40), Vy(40), B(1, 250), Ztel(33), Znme$(42), panel(2, 267)
        'DIM Pz(3021, 2) AS SINGLE
91      OPEN "I", #1, "starsr"
        FOR i = 1 TO 3021
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
        NEXT i
1091    FOR i = 1 TO 241
         INPUT #1, B(0, i)
         INPUT #1, B(1, i)
        NEXT i
1191    FOR i = 0 TO 39
         INPUT #1, P(i, 0)
         INPUT #1, P(i, 4)
         INPUT #1, P(i, 5)
         INPUT #1, P(i, 8)
         INPUT #1, P(i, 9)
         INPUT #1, P(i, 10)
        NEXT i
1291    INPUT #1, year, day, hr, min, sec
        FOR i = 0 TO 35
         INPUT #1, Px(i, 3), Py(i, 3), Vx(i), Vy(i), P(i, 1), P(i, 2)
        NEXT i
1391    FOR i = 0 TO 39
         INPUT #1, Znme$(i)
        NEXT i
1491    FOR i = 1 TO 261
         FOR j = 0 TO 2
          INPUT #1, panel(j, i)
         NEXT j
        NEXT i
        Znme$(40) = "TARGET"
        Znme$(42) = " Vtg"
        Znme$(41) = " Pch"
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        CLOSE #1

     
        'System variables
99      'PRINT FRE(-2)
        'z$ = INPUT$(1)
        eng = 0:    vflag = 0:  Aflag = 0:   Sflag = 0
        mag = 25:   Sangle = 0: cen = 0:     targ = 0:   ref = 3
        trail = 1:  tr = 0:     dte = 0:     ts = .25:   Eflag = 0
        AYSEangle = 0: AYSEscrape = 0: HABrotate% = 0
        ENGsetFLAG = 1
        master = 0
        MODULEflag = 0
        fuel = 2000
        AYSEfuel = 15120000
        AU = 149597890000#
        RAD = 57.295779515#
        G = 6.673E-11
        pi = 3.14159
        pi2 = 2 * pi
        'Px(0, 3) = 0
        'Py(0, 3) = 0
        'Vx(0) = 0
        'Vy(0) = 0
        'P(0, 1) = 0
        'P(0, 2) = 0
        GUIDO$ = ""
       
        'Forced situation file
80      OPEN "I", #1, "orbitstr.txt"
        IF EOF(1) THEN close #1: goto 97
        INPUT #1, suA$
        CLOSE #1
        IF UCASE$(suA$) = "NORMAL" THEN 97
        filename$ = suA$
        OPEN "R", #1, filename$+".RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if len(inpSTR$) <> 1427 then close #1: goto 97
        if chkCHAR1$<>chkCHAR2$ then close #1: goto  97
        if left$(ORBITversion$,5)="XXXXX" then ORBITversion$="ORBIT5S": mid$(inpSTR$,2,7)="ORBIT5S": Put #1, 1, inpSTR$: close #1: goto 52
        close #1
        if ORBITversion$<>"ORBIT5S" then 97
        GOTO 52

97      CLS
        LOCATE 5, 5
        PRINT "Telemetry Echoing Utility for ORBIT v. 5t"
        PRINT
        INPUT ; "    path to main program: ", Zpath$
        IF UCASE$(Zpath$) = "QUIT" THEN END
        filename$="OSBACKUP"
        OPEN "R", #1, filename$+".RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if len(inpSTR$) <> 1427 then 98
        if chkCHAR1$<>chkCHAR2$ then 98
        if ORBITversion$<>"ORBIT5S" then 98
        goto 52
        
98      cls
94      locate 3,20
        print "No valid Telemetry File Found"
95      LOCATE 10, 60: PRINT "Load File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN end
        if ucase$(filename$)="QUIT" then end
        if ucase$(filename$)="Q" then end
        OPEN "R", #1, filename$+".RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if len(inpSTR$) <> 1427 then locate 11,60:print filename$;" is unusable";:goto 96
        if chkCHAR1$<>chkCHAR2$ then locate 11,60:print filename$;" is unusable";:goto 96
        if ORBITversion$<>"ORBIT5S" then locate 11,60:print filename$;" is unusable";:goto 96
        goto 52

96      LOCATE 10, 60: PRINT "                  ";
        GOTO 95



52      GOSUB 807
        CLS
        GOSUB 405
        OLDts = ts

        'Initialize frame rate timer
100     tttt = TIMER
       
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
        RcritL = 0
        COLeventTRIG = 0
        'kknt = kknt + 1
        'IF kknt = 100 THEN kknt = 0: LOCATE 1, 40: PRINT USING "##.#########"; (TIMER - ter) / 100; : ter = TIMER

        'Calculate gravitational acceleration for each object pair
        FOR i = 1 TO 241
         IF B(1, i) = B(0, i) THEN 106
         IF ufo1 = 0 AND (B(1, i) = 38 OR B(0, i) = 38) THEN 106
         IF ufo2 = 0 AND (B(1, i) = 39 OR B(0, i) = 39) THEN 106
         IF B(1, i) = 32 AND AYSE = 150 THEN 106
         difX = Px(B(1, i), 3) - Px(B(0, i), 3)
         difY = Py(B(1, i), 3) - Py(B(0, i), 3)
         GOSUB 5000
         r = SQR((difY ^ 2) + (difX ^ 2))
         IF r < .01 THEN r = .01
         a = G * P(B(0, i), 4) / (r ^ 2)
         P(B(1, i), 1) = P(B(1, i), 1) + (a * SIN(angle))
         P(B(1, i), 2) = P(B(1, i), 2) + (a * COS(angle))
         IF i = 79 OR i = 136 OR i = 195 OR i = 230 THEN GOSUB 166

         IF B(1, i) <> 28 AND B(1, i) <> 32 AND B(1, i) <> 38 THEN 2
         IF (SGN(difX) <> -1 * SGN(Vx(B(1, i)) - Vx(B(0, i)))) OR (SGN(difY) <> -1 * SGN(Vy(B(1, i)) - Vy(B(0, i)))) THEN 2
         Vhab = SQR((Vx(B(1, i)) - Vx(B(0, i))) ^ 2 + (Vy(B(1, i)) - Vy(B(0, i))) ^ 2)
         IF r < ts * Vhab THEN ts = (r - (P(B(0, i), 5) / 2)) / Vhab

2        IF B(1, i) = 32 AND r <= P(B(0, i), 5) + P(32, 5) THEN CONflag2 = 1: CONflag3 = B(0, i): targ = 32
         IF B(1, i) = 28 AND P(B(0, i), 10) > -150 AND r <= P(B(0, i), 5) + P(28, 5) THEN CONflag = 1: CONtarg = B(0, i): Dcon = r: Acon = angle: CONacc = a
         IF B(1, i) = 28 AND B(0, i) <> 32 AND r <= P(B(0, i), 5) + (1000 * P(B(0, i), 10)) THEN atm = B(0, i): Ratm = (r - P(B(0, i), 5)) / 1000
         'IF B(1, i) = 39 AND r <= P(B(0, i), 5) + P(39, 5) THEN explCENTER = 39
         'IF B(1, i) = 38 AND r <= P(B(0, i), 5) + P(38, 5) THEN explCENTER = 38
5        IF B(0, i) = targ AND B(1, i) = 28 THEN Atarg = angle: Dtarg = r: Acctarg = a
6        IF B(0, i) = ref AND B(1, i) = 28 THEN Vref = SQR(G * P(B(0, i), 4) / r): Aref = angle: Dref = r
         IF B(0, i) = Ltr THEN LtrA = a
         IF i = 163 THEN AYSEdist = r
         IF i = 166 THEN OCESSdist = r
106     NEXT i
       

        'Record old center position
101     cenX = Px(cen, 3) + cenXoff
        cenY = Py(cen, 3) + cenYoff
       
        'Erase velocity, approach velocity, and orientation vectors
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (5 * SIN(Sangle)), 120 + (5 * COS(Sangle))), 0
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (10 * SIN(Vvangle)), 120 + (10 * COS(Vvangle))), 0
        IF SQR(((Px(28, 3) - cenX) * mag / AU) ^ 2 + ((Py(28, 3) - cenY) * mag * 1 / AU) ^ 2) > 400 THEN 132
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (20 * SIN(Vvangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (20 * COS(Vvangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 0
       

        'Update object velocities and erase old positions
132     'IF TELEupFLAG = 2 THEN i = 28: GOSUB 301: GOTO 1198
        FOR i = 37 + ufo1 + ufo2 TO 0 STEP -1
         IF i = 28 THEN GOSUB 301
         'IF i = 38 THEN GOSUB 7200
         VxDEL = Vx(i) + (P(i, 1) * OLDts)
         VyDEL = Vy(i) + (P(i, 2) * OLDts)
         IF SQR(VxDEL ^ 2 + VyDEL ^ 2) > 299999999.999# THEN 117
         Vx(i) = VxDEL
         Vy(i) = VyDEL


117      IF i = 36 AND MODULEflag = 0 THEN 108
         IF SQR(((Px(i, 3) - cenX) * mag / AU) ^ 2 + ((Py(i, 3) - cenY) * mag * 1 / AU) ^ 2) - (P(i, 5) * mag / AU) > 400 THEN 108
         IF cen * tr > 0 THEN 108
         IF mag * P(i, 5) / AU > 13200 THEN 118
         'IF mag * P(i, 5) / AU < 1.1 THEN PSET (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag / AU), 8 * trail: GOTO 108
         IF mag * P(i, 5) / AU < 1.1 THEN CIRCLE (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag / AU), 1, 8 * trail: GOTO 108
         clr = 8 * trail
         IF i = 28 THEN vnSa = oldSa: GOSUB 128: GOTO 108
         IF i = 35 THEN GOSUB 138: GOTO 108
         IF i = 37 THEN GOSUB 148: GOTO 108
         IF i = 32 THEN clrMASK = 0: GOSUB 158: GOTO 108
         IF i = 12 AND HPdisp = 1 THEN 108
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
138      FOR j = 215 TO 227 STEP 2
          LINE (300 + (Px(i, 3) - cenX + panel(0, j)) * mag / AU, 220 + (Py(i, 3) - cenY + panel(1, j)) * mag * 1 / AU)-(300 + (Px(i, 3) - cenX + panel(0, j + 1)) * mag / AU, 220 + (Py(i, 3) - cenY + panel(1, 1 + j)) * mag * 1 / AU), clr, B
         NEXT j
         RETURN

         'Paint OCESS
148      PSET (300 + (((Px(37, 3) + panel(0, 229)) - cenX) * mag / AU), 220 + (((Py(37, 3) + panel(1, 229)) - cenY) * mag / AU)), clr
         FOR j = 230 TO 238
          LINE -(300 + (((Px(37, 3) + panel(0, j)) - cenX) * mag / AU), 220 + (((Py(37, 3) + panel(1, j)) - cenY) * mag / AU)), clr
         NEXT j
         RETURN
      
         'Paint AYSE
158      Ax1 = Px(32, 3) + (500 * SIN(AYSEangle + .19 + pi))
         Ax2 = Px(32, 3) + (500 * SIN(AYSEangle - .19 + pi))
         Ay1 = Py(32, 3) + (500 * COS(AYSEangle + .19 + pi))
         Ay2 = Py(32, 3) + (500 * COS(AYSEangle - .19 + pi))
         Ax3 = Px(32, 3) + (95 * SIN(AYSEangle + (pi / 2)))
         Ax4 = Px(32, 3) + (95 * SIN(AYSEangle - (pi / 2)))
         Ay3 = Py(32, 3) + (95 * COS(AYSEangle + (pi / 2)))
         Ay4 = Py(32, 3) + (95 * COS(AYSEangle - (pi / 2)))
         Ax8 = Px(32, 3) + (100095.3 * SIN(AYSEangle + 1.5732935#))
         Ay8 = Py(32, 3) + (100095.3 * COS(AYSEangle + 1.5732935#))
         Ax9 = Px(32, 3) + (100095.3 * SIN(AYSEangle - 1.5732935#))
         Ay9 = Py(32, 3) + (100095.3 * COS(AYSEangle - 1.5732935#))
      
159      Ad1 = SQR((Px(28, 3) - Ax8) ^ 2 + (Py(28, 3) - Ay8) ^ 2)
         Ad2 = SQR((Px(28, 3) - Ax9) ^ 2 + (Py(28, 3) - Ay9) ^ 2)
         ad3 = SQR((Px(28, 3) - Ax1) ^ 2 + (Py(28, 3) - Ay1) ^ 2)
         clr1 = 2
         clr2 = 2
         IF Ad2 < 100090 THEN clr1 = 14
         IF Ad2 < 100085 THEN clr1 = 4
         IF Ad1 < 100090 THEN clr2 = 14
         IF Ad1 < 100085 THEN clr2 = 4
         IF Ad1 > 100080 AND Ad2 > 100080 AND ad3 < 501 GOTO 156
         IF AYSEdist > 580 THEN 156
         AYSEscrape = 10
         Vx(28) = Vx(32)
         Vy(28) = Vy(32)
         IF ad3 > 501 THEN Px(28, 3) = Px(32, 3): Py(28, 3) = Py(32, 3): GOTO 157
         Px(28, 3) = Px(32, 3) + (AYSEdist * SIN(AYSEangle - 3.1415926#))
         Py(28, 3) = Py(32, 3) + (AYSEdist * COS(AYSEangle - 3.1415926#))
157      GOSUB 405
         CONflag = 0

156      IF AYSEdist < 5 THEN clr = 10 ELSE clr = 12
         PSET (300 + ((Ax1 - cenX) * mag / AU), 220 + ((Ay1 - cenY) * mag / AU)), 12
         FOR j = -2.9 TO 2.9 STEP .2
          x = Px(32, 3) + (500 * SIN(j + AYSEangle))
          y = Py(32, 3) + (500 * COS(j + AYSEangle))
          LINE -(300 + ((x - cenX) * mag / AU), 220 + ((y - cenY) * mag / AU)), 12
         NEXT j
         LINE -(300 + ((Ax2 - cenX) * mag / AU), 220 + ((Ay2 - cenY) * mag / AU)), 12
         PSET (300 + ((Ax4 - cenX) * mag / AU), 220 + ((Ay4 - cenY) * mag / AU)), 12
         FOR j = -1.5 TO 1.5 STEP .2
          x = Px(32, 3) + (95 * SIN(j + AYSEangle))
          y = Py(32, 3) + (95 * COS(j + AYSEangle))
          LINE -(300 + ((x - cenX) * mag / AU), 220 + ((y - cenY) * mag / AU)), 12
         NEXT j
         LINE -(300 + ((Ax3 - cenX) * mag / AU), 220 + ((Ay3 - cenY) * mag / AU)), 12
         LINE (300 + ((Ax1 - cenX) * mag / AU), 220 + ((Ay1 - cenY) * mag / AU))-(300 + ((Ax4 - cenX) * mag / AU), 220 + ((Ay4 - cenY) * mag / AU)), 12 * clrMASK
         LINE (300 + ((Ax2 - cenX) * mag / AU), 220 + ((Ay2 - cenY) * mag / AU))-(300 + ((Ax3 - cenX) * mag / AU), 220 + ((Ay3 - cenY) * mag / AU)), 12 * clrMASK
         IF mag < 5E+09 THEN 154
         CIRCLE (300 + ((Ax1 - cenX) * mag / AU), 220 + ((Ay1 - cenY) * mag / AU)), 2, clr1 * clrMASK
         CIRCLE (300 + ((Ax1 - cenX) * mag / AU), 220 + ((Ay1 - cenY) * mag / AU)), 1, clr1 * clrMASK
154      IF mag < 5E+09 THEN 153
         CIRCLE (300 + ((Ax2 - cenX) * mag / AU), 220 + ((Ay2 - cenY) * mag / AU)), 2, clr2 * clrMASK
         CIRCLE (300 + ((Ax2 - cenX) * mag / AU), 220 + ((Ay2 - cenY) * mag / AU)), 1, clr2 * clrMASK
153      RETURN


160     IF mag < 2500000 THEN RETURN
        IF mag > 13812331090.38165# THEN mag = 13812331090.38165#
        IF mag > 4000000000# THEN st = 241 ELSE st = 239
        IF HPdisp = 1 THEN 165
        CLS
        IF cen <> 12 THEN cenXoff = Px(cen, 3) - Px(12, 3): cenYoff = Py(cen, 3) - Py(12, 3)
        cen = 12
        HPdisp = 1
        FOR j = st TO 265
         P1x = 300 + (((Px(12, 3) + (P(12, 5) * panel(1, j))) - cenX) * mag / AU)
         P1y = 220 + (((Py(12, 3) + (P(12, 5) * panel(2, j))) - cenY) * mag / AU)
         P2x = P1x
         P2y = P1y
         IF P2x < 0 THEN P2x = 0
         IF P2x > 639 THEN P2x = 639
         IF P2y < 0 THEN P2y = 0
         IF P2y > 479 THEN P2y = 479
         dist = SQR((P2x - P1x) ^ 2 + (P2y - P1y) ^ 2)
         IF dist > (mag * (panel(0, j) * P(12, 5)) / AU) - 1 THEN 164
         CIRCLE (P1x, P1y), (mag * P(12, 5) * panel(0, j) / AU), 15
         PAINT (P2x, P2y), 0, 15
         PAINT (P2x, P2y), 7, 15
         CIRCLE (P1x, P1y), (mag * P(12, 5) * panel(0, j) / AU), 7
164     NEXT j
        'CIRCLE (300 + ((Px(12, 3) - cenX) * mag / AU), 220 + ((Py(12, 3) - cenY) * mag / AU)), mag * P(12, 5) / AU, 14
        IF DISPflag = 0 THEN LOCATE 7, 2: PRINT "      "; : LOCATE 8, 2: PRINT "      "; : LOCATE 9, 2: PRINT "      ";
        IF DISPflag = 0 THEN GOSUB 400
165     RETURN 109


        'Landing on Hyperion
166     Rmin = 1E+26
        AtargPRIME = angle
        IF ref = 12 AND B(1, i) = 28 THEN Vref = SQR(G * P(B(0, i), 4) / r): Aref = angle: Dref = r
        IF Ltr = 12 THEN LtrA = a
        FOR j = 241 TO 265
          P2x = (Px(12, 3) + (P(12, 5) * panel(1, j)))
          P2y = (Py(12, 3) + (P(12, 5) * panel(2, j)))
          Rcrit = (P(12, 5) * panel(0, j)) + P(B(1, i), 5)
          difX = Px(B(1, i), 3) - P2x
          difY = Py(B(1, i), 3) - P2y
          r = SQR((difY ^ 2) + (difX ^ 2))
          IF r - Rcrit < Rmin THEN Rmin = r - Rcrit: rD = r: PH5prime = P(12, 5) * panel(0, j)
          IF r > Rcrit THEN 167
          IF i = 136 THEN CONflag2 = 1: CONflag3 = 12: targ = 32: RETURN 5
          IF i = 230 THEN RETURN 5
          IF i = 195 THEN RETURN 5
          CONflag = 1: Acon1 = angle: CONacc = a
          RcritL2 = P(12, 5) - PH5prime
          Vx(28) = Vx(12)
          Vy(28) = Vy(12)
          GOSUB 5000
          CONflag = 1: CONtarg = 12: Dcon = r: Acon = angle
          IF r >= Rcrit - .5 THEN 169
          eng = 0: explFLAG1 = 1
          Px(28, 3) = P2x + ((Rcrit - .1) * SIN(Acon + 3.1415926#))
          Py(28, 3) = P2y + ((Rcrit - .1) * COS(Acon + 3.1415926#))
169       IF COS(Acon - Acon1) > 0 THEN 168
          Px(28, 3) = P2x + ((Rcrit + .1) * SIN(Acon + 3.1415926#))
          Py(28, 3) = P2y + ((Rcrit + .1) * COS(Acon + 3.1415926#))
          GOTO 168
167     NEXT j
168     IF i = 79 AND targ = 12 THEN Dtarg = rD: RcritL = P(12, 5) - PH5prime: Atarg = AtargPRIME: Acctarg = a
        RETURN 106


        'Detect contact with an object
102     IF CONflag = 0 THEN 112
        vector = COS(THRUSTangle - Acon)
        IF CONtarg > 37 THEN ufo2 = 0: explFLAG1 = 1: eng = 0: targ = ref: GOTO 112
        IF ((Dcon - P(CONtarg, 5) - P(28, 5)) <= 0) AND ((Aacc + Av + Are) * vector < CONacc * 1.01) THEN Vx(28) = Vx(CONtarg): Vy(28) = Vy(CONtarg)
        IF CONtarg = 12 THEN 112
        IF vector >= 0 THEN 193
         Pvx = P(CONtarg, 4)
         IF Pvx < 1 THEN Pvx = 1
         Vx(CONtarg) = Vx(CONtarg) + (THRUSTx * ts * HABmass / Pvx): Vx(28) = Vx(CONtarg)
         Vy(CONtarg) = Vy(CONtarg) + (THRUSTy * ts * HABmass / Pvx): Vy(28) = Vy(CONtarg)
193     IF ((Dcon - P(CONtarg, 5) - P(28, 5)) > -.5) THEN GOTO 112
        eng = 0
        Px(28, 3) = Px(CONtarg, 3) + ((P(CONtarg, 5) + P(28, 5) - .1) * SIN(Acon + 3.1415926#))
        Py(28, 3) = Py(CONtarg, 3) + ((P(CONtarg, 5) + P(28, 5) - .1) * COS(Acon + 3.1415926#))
       
        'Docked with AYSE drive module
112     IF AYSE = 150 THEN Vx(32) = Vx(28): Vy(32) = Vy(28): Px(32, 3) = Px(28, 3): Py(32, 3) = Py(28, 3): AYSEangle = Sangle
        IF CONflag2 = 1 AND CONflag4 = 0 THEN CONflag4 = 1
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
     

        'Record telemetry to a file
111     IF ts > .3 THEN UDstep = .01 ELSE UDstep = 1
        IF TELEflag = 1 AND TIMER - TELEbk > UDstep THEN TELEbk = TIMER: PRINT #2, Px(28, 3) - Px(ref, 3), Py(28, 3) - Py(ref, 3), Vrefhab

        'Repaint objects to the screen
191     FOR i = 37 + ufo1 + ufo2 TO 0 STEP -1
         IF i = 36 AND MODULEflag = 0 THEN 109
         IF SQR(((Px(i, 3) - cenX) * mag / AU) ^ 2 + ((Py(i, 3) - cenY) * mag * 1 / AU) ^ 2) - (P(i, 5) * mag / AU) > 400 THEN 109
         IF mag * P(i, 5) / AU > 13200 THEN 119
         pld = 0
         IF i = 28 THEN pld = 2 * ABS(SGN(eng))
         'IF mag * P(i, 5) / AU < 1.1 THEN PSET (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), P(i, 0) + pld: GOTO 109
         IF mag * P(i, 5) / AU < 1.1 THEN CIRCLE (300 + (Px(i, 3) - cenX) * mag / AU, 220 + (Py(i, 3) - cenY) * mag * 1 / AU), 1, P(i, 0) + pld: GOTO 109
         IF i = 28 THEN clr = 12 + pld: vnSa = Sangle: GOSUB 128: GOTO 109
         IF i = 35 THEN clr = 12: GOSUB 138: GOTO 109
         IF i = 37 THEN clr = 12: GOSUB 148: GOTO 109
         IF i = 32 THEN clrMASK = 1: GOSUB 158: GOTO 109
         IF i = 12 THEN GOSUB 160
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
        IF telTRACK = 1 THEN GOSUB 6050
               
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (10 * SIN(Vvangle)), 120 + (10 * COS(Vvangle))), 12
        IF DISPflag = 0 THEN LINE (30, 120)-(30 + (5 * SIN(Sangle)), 120 + (5 * COS(Sangle))), 10
        IF DISPflag = 0 THEN PSET (30, 120), 1
        IF SQR(((Px(28, 3) - cenX) * mag / AU) ^ 2 + ((Py(28, 3) - cenY) * mag * 1 / AU) ^ 2) > 400 THEN 133
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (30 * SIN(Atarg)) + (Px(28, 3) - cenX) * mag / AU, 220 + (30 * COS(Atarg)) + (Py(28, 3) - cenY) * mag * 1 / AU), 8
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (20 * SIN(Vvangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (20 * COS(Vvangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 12
        IF vflag = 1 THEN LINE (300 + (Px(28, 3) - cenX) * mag / AU, 220 + (Py(28, 3) - cenY) * mag * 1 / AU)-(300 + (10 * SIN(Sangle)) + (Px(28, 3) - cenX) * mag / AU, 220 + (10 * COS(Sangle)) + (Py(28, 3) - cenY) * mag * 1 / AU), 10
133     VangleDIFF = Atarg - Vvangle
       
        'Refueling
        if PAUSEflag = 1 then 123
        IF TELEupFLAG <> 1 THEN 134
        fuel = fuel + (refuel * 100) - (ventfuel * 100)
        IF fuel > 200000 THEN fuel = 200000: refuel = 0
        IF fuel < 0 THEN fuel = 0: ventfuel = 0
        AYSEfuel = AYSEfuel + (AYSErefuel * 1000) - (1000 * AYSEventfuel)
        IF AYSEfuel > 20000000 THEN AYSEfuel = 20000000
        IF AYSEfuel < 0 THEN AYSEfuel = 0

        'Update simulation time
134     IF TELEupFLAG = 2 THEN 1121
        sec = sec + ts
        IF sec > 60 THEN min = min + 1: sec = sec - 60
        IF min = 60 THEN hr = hr + 1: min = 0
        IF hr = 24 THEN day = day + 1: hr = 0
        dayNUM = 365
        IF INT(year / 4) * 4 = year THEN dayNUM = 366
        IF INT(year / 100) * 100 = year THEN dayNUM = 365
        IF INT(year / 400) * 400 = year THEN dayNUM = 366
        IF day = dayNUM + 1 THEN year = year + 1: day = 1
       
1121    IF dte = 0 AND ts > .25 THEN 121
        LOCATE 25, 61
        IF TELEMflag = 0 OR TELEupFLAG = 1 THEN PRINT USING "####"; year;  ELSE PRINT "TELM";
        LOCATE 25, 66
        IF TELEMflag = 0 OR TELEupFLAG = 1 THEN PRINT USING "###"; day;  ELSE PRINT "ERR";
        PRINT USING "###"; hr; min;
        IF ts < 60 THEN LOCATE 25, 75: PRINT USING "###"; sec;
       
        'Print Simulation data
121     IF targ = 40 THEN 123
        IF COS(VangleDIFF) <> 0 AND Dtarg - P(targ, 5) <> 0 THEN Acctarg = Acctarg + ((((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2) / (2 * (Dtarg - P(targ, 5)))) * COS(VangleDIFF))
123     oldAcctarg = Acctarg
        IF DISPflag = 1 THEN 113
        COLOR 12
        LOCATE 8, 16: IF CONSTacc = 1 THEN PRINT CHR$(67 + (10 * MATCHacc));  ELSE PRINT " ";
        COLOR 15
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
        IF Dtarg > 9.9E+11 THEN PRINT USING "##.########^^^^"; (Dtarg - P(targ, 5) - P(28, 5) + RcritL) / 1000;  ELSE PRINT USING "###,###,###.###"; (Dtarg - P(targ, 5) - P(28, 5) + RcritL) / 1000;
        LOCATE 15, 9: PRINT USING "####.##"; Atargref * RAD;

        IF Cdh > .0005 THEN COLOR 14
        LOCATE 7, 8: IF Cdh < .0005 THEN PRINT USING "#####.###"; Are;  ELSE PRINT USING "#####.##"; Are; : PRINT "P";
        COLOR 15
        LOCATE 8, 8: PRINT USING "#####.##"; Aacc;
        LOCATE 11, 6
        IF Dfuel = 0 THEN PRINT "H"; : PRINT USING "#########"; fuel; : PRINT CHR$(32 + (refuel * 11) + (ventfuel * 13));
        IF Dfuel = 1 THEN PRINT "A"; : PRINT USING "#########"; AYSEfuel; : PRINT CHR$(32 + (AYSErefuel * 11) + (AYSEventfuel * 13));
        IF Dfuel = 2 THEN PRINT "RCS"; : PRINT USING "#######"; vernP!;
        LOCATE 18, 9: PRINT USING "####.##"; DIFFangle;
        IF TELEupFLAG = 1 THEN LOCATE 23, 66: PRINT "TELEMETRY OFF";
        IF TELEupFLAG = 2 THEN LOCATE 23, 66: PRINT "TELEM ONLY   ";
        IF TELEflag = 1 THEN LOCATE 22, 66: PRINT "REC: "; filename$;

        COLOR 15
124     GOSUB 3005
        GOSUB 3008
        GOSUB 3006
        if PAUSEflag = 1 then 103
                             
       
        'Timed Telemetry Retreival
        IF bkt - TIMER > 120 THEN bkt = TIMER
        IF TELEupFLAG = 1 THEN bkt = TIMER
1198    IF bkt + 1 < TIMER THEN bkt = TIMER: GOSUB 800: OLDts = ts: restoreFLAG = 0: GOTO 100


113     IF COLeventTRIG = 1 THEN ts = .125
        OLDts = ts
        

        'Control input
103     z$ = INKEY$
        IF z$ = "" THEN 105
        IF z$ = "q" THEN GOSUB 900
        IF z$ = "`" THEN DISPflag = 1 - DISPflag: CLS : IF DISPflag = 0 THEN GOSUB 405
        'IF z$ = CHR$(27) THEN GOSUB 910
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
       
        IF z$ = "e" THEN ENGsetFLAG = 1 - ENGsetFLAG
        IF z$ = "w" THEN SRBtimer = 120
        IF z$ = "a" THEN AYSE = 150 - AYSE
        IF z$ = "g" THEN CHUTE = 1 - CHUTE
        IF z$ = "k" THEN GOSUB 3200
        IF z$ = "+" AND mag < 130000000000# THEN mag = mag / .75: CLS : GOSUB 405
        IF z$ = "-" AND mag > 6.8E-11 THEN mag = mag * .75: CLS : GOSUB 405
        IF z$ = CHR$(0) + "I" THEN HABrotate% = HABrotate% - 1: vernP! = vernP! - 1
        IF z$ = CHR$(0) + "G" THEN HABrotate% = HABrotate% + 1: vernP! = vernP! - 1
                                                                           

        IF z$ = "[" THEN GOSUB 460
        IF z$ = "]" THEN GOSUB 465
        IF z$ < "0" OR z$ > "U" THEN 110
        z = ASC(z$) - 48
        IF z = 36 AND MODULEflag = 0 THEN 110
        IF Aflag = 0 THEN cen = z: CLS : cenXoff = 0: cenYoff = 0: GOSUB 405
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
        IF z$ = "l" THEN ORref = 1 - ORref: CLS : GOSUB 405
        IF z$ = CHR$(0) + "@" THEN Sflag = 7: angleOFFSET = (Atarg - Sangle): GOSUB 400
        IF z$ = "u" THEN tr = 1 - tr: CLS : GOSUB 400
        IF z$ = "d" THEN dte = 1 - dte: GOSUB 400
        IF z$ = "p" THEN PROJflag = 1 - PROJflag: GOSUB 400
        IF z$ = "{" THEN ventfuel = 1 - ventfuel: refuel = 0
        IF z$ = "}" THEN refuel = 1 - refuel: ventfuel = 0
        IF z$ = "(" THEN AYSEventfuel = 1 - AYSEventfuel: AYSErefuel = 0
        IF z$ = ")" THEN AYSErefuel = 1 - AYSErefuel: AYSEventfuel = 0
        IF z$ = "o" THEN GOSUB 3000
        IF z$ = "c" AND telTRACK = 1 THEN CLOSE #2: telTRACK = 0
        IF z$ = "c" THEN GOSUB 405
        IF z$ = "x" THEN TELEupFLAG = TELEupFLAG + 1: IF TELEupFLAG = 3 THEN TELEupFLAG = 0
        IF z$ = "x" AND TELEupFLAG = 0 THEN LOCATE 23, 66: PRINT "             ";
        IF z$ = "Z" THEN TELEflag = 0: telTRACK = 0: CLOSE #2: GOSUB 6000
        IF z$ = "z" THEN TELEflag = 0: telTRACK = 0: CLOSE #2: GOSUB 6005
        IF z$ = "y" THEN GOSUB 6100: CLS : GOSUB 405
        if z$ = "X" THEN PAUSEflag=1-PAUSEflag:goto 103
    
       
        IF z$ = "Y" THEN ii = 3: ij = 35: im = 365000: GOSUB 3101: ii = 3: ij = 32: im = 565000: GOSUB 3101
        IF z$ = "," THEN bkt = bkt - .1
        IF z$ = "." THEN bkt = bkt + .1
        IF z$ <> "/" THEN 104
        IF ts < .375 THEN ts = ts / 2: GOSUB 400
        IF ts = .375 THEN ts = .25: GOSUB 400
        IF ts = .5 THEN ts = .375: GOSUB 400
        IF ts = 1 THEN ts = .5: GOSUB 400
        IF ts = 2 THEN ts = 1: GOSUB 400
        IF ts = 10 THEN ts = 2: GOSUB 400
        IF ts > 10 THEN ts = ts - 10: GOSUB 400
104     IF z$ <> "*" THEN 105
        IF ts > 9 THEN ts = ts + 10: GOSUB 400
        IF ts = 2 THEN ts = 10: GOSUB 400
        IF ts = 1 THEN ts = 2: GOSUB 400
        IF ts = .5 THEN ts = 1: GOSUB 400
        IF ts = .375 THEN ts = .5: GOSUB 400
        IF ABS(ts - .25) < .05 THEN ts = .375: GOSUB 400
        IF ts < .25 THEN ts = ts * 2: GOSUB 400
105     IF z$ = "s" THEN GOSUB 600
        IF z$ = "r" THEN GOSUB 700
        IF tttt - TIMER > ts * 10 THEN tttt = TIMER + (ts / 2)
        IF ts < .3 AND TIMER - tttt < ts THEN 103
        if PAUSEflag = 1 and z$ = "" then 103
        if PAUSEflag = 1 then cenX = Px(cen, 3) + cenXoff: cenY = Py(cen, 3) + cenYoff: goto 191
        IF TELEupFLAG = 2 THEN 1198 ELSE 100


        'SUBROUTINE Automatic space craft orientation calculations
301     IF Ztel(1) = 1 AND TELEupFLG = 0 THEN Sflag = 1: MATCHacc = 0: CONSTacc = 0
        IF TELEupFLAG <> 1 THEN 303
        IF AYSE = 150 THEN Ztel(2) = 6.4E+07 ELSE Ztel(2) = 43750
        IF CHUTE = 1 THEN Cdh = .0006 ELSE Cdh = .0002
        IF SRBtimer > 0 THEN SRB = 131250 ELSE SRB = 0
        IF SRBtimer > 0 THEN SRBtimer = SRBtimer - ts


303     COLOR 15
        Aoffset = ATN((P(targ, 5) * 1.01) / (Dtarg + .0001)): Atarg = Atarg - (Aoffset * OFFSET)
        difX = Vx(targ) - Vx(28)
        difY = Vy(targ) - Vy(28)
        GOSUB 5000
        Vvtangle = angle
        IF ORref = 1 THEN Aa = Atarg ELSE Aa = Aref
        IF PROJflag = 0 THEN DIFFangle = (Aa - Sangle) * RAD ELSE DIFFangle = (Atarg - Vvtangle) * RAD
        IF DIFFangle > 180 THEN DIFFangle = -360 + DIFFangle
        IF DIFFangle < -180 THEN DIFFangle = 360 + DIFFangle
       
        difX = Px(28, 3) - Px(Wind1, 3)
        difY = Py(28, 3) - Py(Wind1, 3)
        GOSUB 5000
        Wangle = angle
        VwindX = (Wind2 * SIN(Wangle + Wind3))
        VwindY = (Wind2 * COS(Wangle + Wind3))

        IF Sflag = 1 THEN Sangle = Sangle + (HABrotate% * .0086853 * ts): GOTO 302
        HABrotate% = 0
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
        LOCATE 5, 16: COLOR 8 + (7 * ENGsetFLAG): PRINT USING "####.#"; eng;
        IF Sflag <> 1 THEN 307
        IF HABrotate% <> 0 THEN COLOR 15 ELSE COLOR 8
        LOCATE 25, 15: PRINT USING "##.#"; ABS(HABrotate%) / 2;
        If (NAVmalf and 11264)>0 then color 12:rotSYMB$=">" else color 10:rotSYMB$=" "
        LOCATE 25, 19: IF HABrotate% < 0 THEN PRINT ">";  ELSE PRINT rotSYMB$;
        If (NAVmalf and 4864)>0 then color 12:rotSYMB$="<" else color 10:rotSYMB$=" "
        LOCATE 25, 14: IF HABrotate% > 0 THEN PRINT "<";  ELSE PRINT rotSYMB$;       
307     COLOR 15
        IF Ztel(2) = 0 THEN MATCHacc = 0: CONSTacc = 0
        IF MATCHacc = 1 THEN Accel = oldAcctarg
        HABmass = 275000 + fuel
        IF AYSE = 150 THEN HABmass = HABmass + 20000000 + AYSEfuel
        massDEL = (1 - ((Vx(28) ^ 2 + Vy(28) ^ 2) / 300000000 ^ 2))
        IF massDEL < 9.999946E-41 THEN massDEL = 9.999946E-41
        HABmass = HABmass / SQR(massDEL)
        IF CONSTacc = 1 THEN Aacc = Accel: eng = ENGsetFLAG * Aacc * HABmass / Ztel(2) ELSE Aacc = ENGsetFLAG * (Ztel(2) * eng) / HABmass
        Av = (175000 * vern) / HABmass
        IF AYSE = 150 THEN Av = 0
        vern = 0

304     IF TELEupFLAG = 1 THEN SRB = 131250 * SGN(SRBtimer) ELSE SRBtimer = 0
        Aacc = Aacc + (SRB / HABmass) * 100
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
        AOA = ((COS(VvRangle - Sangle))) * SGN(SGN(COS(VvRangle - Sangle)) - 1)
        AOA = AOA * AOA * AOA
        'LOCATE 5, 38: PRINT "  "; : PRINT USING "####.####"; RAD * (VvRangle - Sangle);
        'LOCATE 6, 40: PRINT "  "; : PRINT USING "##.####"; AOA;
        IF AOA > .5 THEN AOA = 1 - AOA
        AOA = (AOA * SGN(SIN(VvRangle - Sangle))) * .5
        AOAx = -1 * ABS(AOA) * SIN(VvRangle + (1.5708 * SGN(AOA)))
        AOAy = -1 * ABS(AOA) * COS(VvRangle + (1.5708 * SGN(AOA)))
        
        'LOCATE 2, 40: PRINT "X:"; : PRINT USING "##.####"; AOAx;
        'LOCATE 3, 40: PRINT "Y:"; : PRINT USING "##.####"; AOAy;
        'LOCATE 1, 40: PRINT "  "; : PRINT USING "##.####"; AOA;
        VVr = SQR((difX ^ 2) + (difY ^ 2))
        IF atm = 40 THEN Pr = .01: GOTO 320
        IF Ratm < 0 THEN Pr = P(atm, 8) ELSE Pr = P(atm, 8) * (2.71828 ^ (-1 * Ratm / P(atm, 9)))
320     IF TELEupFLAG = 1 THEN Cdh = .0002 + (CHUTE * .0004)
        Are = Pr * VVr * VVr * Cdh
        IF Are * ts > VVr / 2 THEN Are = (VVr / 2) / ts
        IF CONflag = 1 AND Wind3 = 0 THEN Are = 0
        P(i, 1) = P(i, 1) - (Are * SIN(VvRangle)) + (Are * AOAx)
        P(i, 2) = P(i, 2) - (Are * COS(VvRangle)) + (Are * AOAy)
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
       
        IF TELEupFLAG <> 1 THEN 325
        IF SRBtimer < 0 THEN SRBtimer = 0
        IF AYSE = 150 THEN AYSEfuel = AYSEfuel - ABS(ENGsetFLAG * .1755 * eng * ts) ELSE fuel = fuel - ABS(ENGsetFLAG * .04824 * eng * ts)

325     RETURN


       
        'SUBROUTINE print control variable names to screen
405     CLS
        HPdisp = 0
400     'IF mag < .1 THEN GOSUB 8000
        IF ts < .015625 THEN ts = .015625
        IF ts > 60 THEN ts = 60
        IF Dfuel > 2 THEN Dfuel = 0
        IF ufo2 = 1 THEN ts = .25
        COLOR 8
        FOR j = 1 TO 214
         LOCATE panel(0, j), panel(1, j): PRINT CHR$(panel(2, j));
         IF dte = 0 AND j = 168 THEN 403
        NEXT j
403     COLOR 7
        IF Ztel(1) = 1 THEN Sflag = 1
        LOCATE 2, 2: PRINT "ref Vo";
        LOCATE 3, 2: PRINT "V hab-ref";
        LOCATE 4, 2: PRINT "Vtarg-ref";
        COLOR 7 '+ (5 * SGN(Ztel(2)))
        LOCATE 5, 2: PRINT "Engine"; : LOCATE 5, 16: COLOR 8 + (7 * ENGsetFLAG): PRINT USING "####.#"; eng;
        COLOR 7 '+ (5 * Ztel(1))
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
        IF telTRACK = 1 THEN LOCATE 21, 59: PRINT "TRACK DEV          km"; : LOCATE 22, 59: PRINT "Speed Dev         m/s";
        COLOR 15
402     RETURN



460     ON Aflag + 1 GOTO 461, 462, 463
461     IF cen = 40 THEN cen = 38
        IF cen - 1 = 36 AND MODULEflag = 0 THEN cen = 36
        IF cen - 1 < 0 THEN cen = 41
        cen = cen - 1
        CLS
        cenXoff = 0
        cenYoff = 0
        GOSUB 405
        RETURN

462     IF targ - 1 = 28 THEN targ = 28
        IF targ - 1 = 36 AND MODULEflag = 0 THEN targ = 36
        IF targ - 1 < 0 THEN targ = 41
        IF targ = 40 THEN targ = 38 + ufo1 + ufo2
        targ = targ - 1
        GOSUB 400
        RETURN
        

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
        GOSUB 405
        RETURN

467     IF targ = 40 THEN targ = -1
        IF targ + 1 = 28 THEN targ = 28
        IF targ + 1 = 36 AND MODULEflag = 0 THEN targ = 36
        IF targ + 1 > 37 + ufo1 + ufo2 THEN targ = 39
        targ = targ + 1
        GOSUB 400
        RETURN
        GOTO 469

468     IF ref + 1 = 28 THEN ref = 28
        IF ref + 1 = 35 THEN ref = -1
        IF ref + 1 > 37 THEN ref = 36
        ref = ref + 1
469     GOSUB 400
        RETURN


        'SUBROUTINE save data to file
600     LOCATE 9, 60: PRINT "8 charaters a-z 0-9";
        LOCATE 10, 60: PRINT "Save File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN CLS : GOSUB 405: RETURN
        OPEN "R", #1, filename$+".rnd",1427
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
        chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$ = chr$(chkBYTE+64)
        outSTR$ = outSTR$ + "ORBIT5S        "
        outSTR$ = outSTR$ + mks$(eng)
        outSTR$ = outSTR$ + mki$(vflag)
        outSTR$ = outSTR$ + mki$(Aflag)
        outSTR$ = outSTR$ + mki$(Sflag)
        outSTR$ = outSTR$ + mkd$(Are)
        outSTR$ = outSTR$ + mkd$(mag)
        outSTR$ = outSTR$ + mks$(Sangle)
        outSTR$ = outSTR$ + mki$(cen)
        outSTR$ = outSTR$ + mki$(targ)
        outSTR$ = outSTR$ + mki$(ref)
        outSTR$ = outSTR$ + mki$(trail)
        outSTR$ = outSTR$ + mks$(Cdh)
        outSTR$ = outSTR$ + mks$(SRB)
        outSTR$ = outSTR$ + mki$(tr)
        outSTR$ = outSTR$ + mki$(dte)
        outSTR$ = outSTR$ + mkd$(ts)
        outSTR$ = outSTR$ + mkd$(OLDts)
        outSTR$ = outSTR$ + mks$(vernP!)
        outSTR$ = outSTR$ + mki$(Eflag)
        outSTR$ = outSTR$ + mki$(year)
        outSTR$ = outSTR$ + mki$(day)
        outSTR$ = outSTR$ + mki$(hr)
        outSTR$ = outSTR$ + mki$(min)
        outSTR$ = outSTR$ + mkd$(sec)
        outSTR$ = outSTR$ + mks$(AYSEangle)
        outSTR$ = outSTR$ + mki$(AYSEscrape)
        outSTR$ = outSTR$ + mks$(Ztel(15))
        outSTR$ = outSTR$ + mks$(Ztel(16))
        outSTR$ = outSTR$ + mks$(HABrotate)
        outSTR$ = outSTR$ + mki$(AYSE)
        outSTR$ = outSTR$ + mks$(Ztel(9))
        outSTR$ = outSTR$ + mki$(MODULEflag)
        outSTR$ = outSTR$ + mks$(AYSEdist)
        outSTR$ = outSTR$ + mks$(OCESSdist)
        outSTR$ = outSTR$ + mki$(explosion)
        outSTR$ = outSTR$ + mki$(explosion1)
        outSTR$ = outSTR$ + mks$(Ztel(1))
        outSTR$ = outSTR$ + mks$(Ztel(2))
        outSTR$ = outSTR$ + mkl$(NAVmalf)
        outSTR$ = outSTR$ + mks$(Ztel(14))
        outSTR$ = outSTR$ + mks$(LONGtarg)
        outSTR$ = outSTR$ + mks$(Pr)
        outSTR$ = outSTR$ + mks$(Agrav)
        FOR i = 1 TO 39
         outSTR$ = outSTR$ + mkd$(Px(i,3))
         outSTR$ = outSTR$ + mkd$(Py(i,3))
         outSTR$ = outSTR$ + mkd$(Vx(i))
         outSTR$ = outSTR$ + mkd$(Vy(i))
        NEXT i
        outSTR$ = outSTR$ + mks$(fuel)
        outSTR$ = outSTR$ + mks$(AYSEfuel)
        outSTR$ = outSTR$ + chr$(chkBYTE+64)
        open "R", #1, filename$+".RND", 1427
        put #1, 1, outSTR$
        CLOSE #1
620     CLS
        GOSUB 405
        RETURN
       

        'SUBROUTINE: Restore data from saved file
700     LOCATE 10, 60: PRINT "Load File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN locate 10, 60: print space$(20);:return
        goto 801
702     LOCATE 10, 60: PRINT "                  ";
        GOTO 700

        'SUBROUTINE: Timed telemetry retrieval
800     filename$="OSBACKUP"
801     k=1
802     OPEN "R", #1, filename$+".RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if filename$="OSBACKUP" then 809
        if len(inpSTR$) <> 1427 then locate 11,60:print filename$;" is unusable";:goto 702
        if chkCHAR1$<>chkCHAR2$ then locate 11,60:print filename$;" is unusable";:goto 702
        if ORBITversion$<>"ORBIT5S" then locate 11,60:print filename$;" is unusable";:goto 702
        goto 807

809     if len(inpSTR$) <> 1427 then TELEMflag = 1:return
        IF ORBITversion$ = "XXXXXXX" THEN open "O", #1, "orbitstr.txt": print #1, "OSBACKUP": close #1: RUN "orbit5vm" 
        IF ORBITversion$ <> "ORBIT5S" THEN TELEMflag = 1:return
        if chkCHAR1$=chkCHAR2$ then 807
        k=k+1
        if k<4 then 802
        tttt = TIMER + .8
        TELEMflag = 1:return
        
807     k=89
        year = cvi(mid$(inpSTR$,k,2)):k=k+2
        day = cvi(mid$(inpSTR$,k,2)):k=k+2
        hr = cvi(mid$(inpSTR$,k,2)):k=k+2
        min = cvi(mid$(inpSTR$,k,2)):k=k+2
        sec = cvd(mid$(inpSTR$,k,8))
        if filename$<>"OSBACKUP" then 808
        TELEMflag = 0
        IF year = zt16 AND day = zt17 AND hr = zt18 AND min = zt19 AND sec = zt20 THEN TELEMflag = 1
        zt16 = year
        zt17 = day
        zt18 = hr
        zt19 = min
        zt20 = sec
        IF TELEMflag = 1 AND TELEupFLAG = 0 THEN 806

808     k=2+15
        eng = cvs(mid$(inpSTR$,k,4)):k=k+8
        'vflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        'Aflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Sflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Are = cvd(mid$(inpSTR$,k,8)):k=k+16
        'mag = cvd(mid$(inpSTR$,k,8)):k=k+8
        Sangle = cvs(mid$(inpSTR$,k,4)):k=k+6
        'cen = cvi(mid$(inpSTR$,k,2)):k=k+2
        targ = cvi(mid$(inpSTR$,k,2)):k=k+2
        ref = cvi(mid$(inpSTR$,k,2)):k=k+4
        'trail=cvi(mid$(inpSTR$,k,2)):k=k+2
        Cdh = cvs(mid$(inpSTR$,k,4)):k=k+4
        SRB = cvs(mid$(inpSTR$,k,4)):k=k+8
        'tr = cvi(mid$(inpSTR$,k,2)):k=k+2
        'dte = cvi(mid$(inpSTR$,k,2)):k=k+2
        ts = cvd(mid$(inpSTR$,k,8)):k=k+8
        OLDts = cvd(mid$(inpSTR$,k,8)):k=k+8
        vernP! = cvs(mid$(inpSTR$,k,4)):k=k+22
        'Eflag = cvi(mid$(inpSTR$,k,2)):k=k+2+16
        AYSEangle = cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEscrape = cvi(mid$(inpSTR$,k,2)):k=k+2
        Wind2 = cvs(mid$(inpSTR$,k,4)):k=k+4
        Wind3 = cvs(mid$(inpSTR$,k,4)):k=k+4
        HABrotate% = cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSE = cvi(mid$(inpSTR$,k,2)):k=k+2
        Ztel(9) = cvs(mid$(inpSTR$,k,4)):k=k+4
        MODULEflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        AYSEdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        OCESSdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        explosion = cvi(mid$(inpSTR$,k,2)):k=k+2
        explosion1 = cvi(mid$(inpSTR$,k,2)):k=k+2
        Ztel(1) = cvs(mid$(inpSTR$,k,4)):k=k+4
        Ztel(2) = cvs(mid$(inpSTR$,k,4)):k=k+4
        NAVmalf = cvl(mid$(inpSTR$,k,4)):k=k+4
        Wind1 = cvs(mid$(inpSTR$,k,4)):k=k+4
        LONGtarg = cvs(mid$(inpSTR$,k,4)):k=k+4
        Pr = cvs(mid$(inpSTR$,k,4)):k=k+4
        Agrav = cvs(mid$(inpSTR$,k,4)):k=k+4
        FOR i = 1 TO 39
         Px(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Py(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Vx(i) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Vy(i) = cvd(mid$(inpSTR$,k,8)):k=k+8
        NEXT i
        fuel = cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEfuel = cvs(mid$(inpSTR$,k,4)):k=k+4
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        ufo1 = 0
        ufo2 = 0
        IF Px(39, 3) <> 0 AND Py(39, 3) <> 0 THEN ufo2 = 1
        IF Px(38, 3) <> 0 AND Py(38, 3) <> 0 THEN ufo1 = 1
        Ltx = (P(ref, 5) * SIN(LONGtarg))
        Lty = (P(ref, 5) * COS(LONGtarg))
        Ltr = ref
        'if OLDchkCHAR$=chkCHAR1$ then TELEMflag = 1
        'OLDchkCHAR$=chkCHAR1$
806     RETURN


        'Confirm end program
900     LOCATE 10, 60: INPUT ; "End Program "; z$
        IF UCASE$(z$) = "Y" THEN run "orbit5vS"
        LOCATE 10, 60: PRINT "                   ";
        RETURN

        'Name and author
'910     LOCATE 2, 60: PRINT "OCESS Orbit 5 T  ";
'        LOCATE 3, 60: PRINT CHR$(74); CHR$(97); CHR$(109); CHR$(101); CHR$(115); " "; CHR$(77); CHR$(97); CHR$(103); CHR$(119); CHR$(111); CHR$(111); CHR$(100);
'        RETURN

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
        IF ABS(ecc) < .0000001 THEN ecc = SGN(ecc) * .0000001#
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
        IF orbE# = 0 THEN LOCATE 20, 7: PRINT SPACE$(9); : LOCATE 19, 7: PRINT SPACE$(9); : GOTO 3007
        orbA = orbD# / ABS(2 * orbE#)
        PROJmax = orbA * (1 + ecc)
        PROJmin = orbA * (1 - ecc)
        IF ecc = 1 THEN PROJmin = orbA
        IF ecc > 1 THEN PROJmin = orbA * (ecc - 1)
        IF DISPflag = 1 THEN RETURN
        LOCATE 19, 7
        PROJmin = (PROJmin - P(ORrefOBJ, 5)) / 1000
        PROJmax = (PROJmax - P(ORrefOBJ, 5)) / 1000
        IF ABS(PROJmin) > 899999 THEN PRINT USING "##.##^^^^"; PROJmin;  ELSE PRINT USING "######.##"; PROJmin;
        LOCATE 20, 7
        IF ecc >= 1 THEN PRINT "  -------"; : GOTO 3007
        IF ABS(PROJmax) > 899999 THEN PRINT USING "##.##^^^^"; PROJmax;  ELSE PRINT USING "######.##"; PROJmax;
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
3100    ii = 3
        ij = 35
        im = 365000
        'ii = 3
        'ij = 32
        'im = 567000
3101    difX = Px(ii, 3) - Px(ij, 3)
        difY = Py(ii, 3) - Py(ij, 3)
        GOSUB 5000
        Px(ij, 3) = Px(ii, 3) + ((P(ii, 5) + im) * SIN(angle))
        Py(ij, 3) = Py(ii, 3) + ((P(ii, 5) + im) * COS(angle))
        Vx(ij) = Vx(ii) + (SIN(angle + 1.570796) * SQR(G * P(ii, 4) / (P(ii, 5) + im)))
        Vy(ij) = Vy(ii) + (COS(angle + 1.570796) * SQR(G * P(ii, 4) / (P(ii, 5) + im)))
        'Px(32, 3) = Px(28, 3)
        'Py(32, 3) = Py(28, 3)
        'Vx(32) = Vx(28)
        'Vy(32) = Vy(28)
        RETURN

3200    IF CONflag = 0 THEN 3299
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
        GOSUB 405
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


        'Display Recorded Track
6000    LOCATE 10, 60: PRINT "Load File: "; : INPUT ; "", GUIDO$
        CLS
        GOSUB 400
6005    IF GUIDO$ = "" THEN 6003
        OPEN "R", #2, GUIDO$
        IF LOF(2) > 1 THEN CLOSE #2: GOTO 6006
        CLOSE #2
        GOTO 6003
6006    OPEN "I", #2, GUIDO$
        IF EOF(2) THEN 6002
        INPUT #2, teleX
        IF EOF(2) THEN 6002
        INPUT #2, teleY
        IF EOF(2) THEN 6002
        INPUT #2, teleV
        Xold = 300 + ((Px(ref, 3) + teleX) - cenX) * mag / AU
        Yold = 220 + ((Py(ref, 3) + teleY) - cenY) * mag * 1 / AU
6001    IF EOF(2) THEN 6002
        INPUT #2, teleX
        IF EOF(2) THEN 6002
        INPUT #2, teleY
        IF EOF(2) THEN 6002
        INPUT #2, teleV
        Xnew = 300 + ((Px(ref, 3) + teleX) - cenX) * mag / AU
        Ynew = 220 + ((Py(ref, 3) + teleY) - cenY) * mag * 1 / AU
        IF Xold > 10000 THEN 6004
        IF Yold > 10000 THEN 6004
        IF Xnew > 10000 THEN 6004
        IF Ynew > 10000 THEN 6004
        LINE (Xold, Yold)-(Xnew, Ynew), 10
6004    Xold = Xnew
        Yold = Ynew
        GOTO 6001
6002    CLOSE #2
        OPEN "I", #2, GUIDO$
        INPUT #2, telX1
        INPUT #2, telY1
        INPUT #2, telV1
        INPUT #2, telX2
        INPUT #2, telY2
        INPUT #2, telV2
        telTRACK = 1
        LOCATE 21, 59: PRINT "Track Dev          km";
        LOCATE 22, 59: PRINT "Speed Dev         m/s";
6003    RETURN
   
        'Calculate distance from track
6050    x = Px(28, 3) - Px(ref, 3)
        y = Py(28, 3) - Py(ref, 3)
6053    u = ((x - telX1) * (telX2 - telX1)) + ((y - telY1) * (telY2 - telY1))
        DEL = ((telX1 - telX2) ^ 2) + ((telY1 - telY2) ^ 2)
        IF DEL = 0 THEN 6060
        u = u / DEL
        DEL = SQR(DEL)
        x1 = telX1 + (u * (telX2 - telX1))
        y1 = telY1 + (u * (telY2 - telY1))
        del1 = SQR(((telX1 - x1) ^ 2) + ((telY1 - y1) ^ 2))
        del2 = SQR(((telX2 - x1) ^ 2) + ((telY2 - y1) ^ 2))
        'IF del1 < del2 AND del2 > DEL THEN x1 = telX1: y1 = telY1: GOTO 6051
        IF del1 > del2 AND del1 > DEL THEN 6060
        delV = telV2 - telV1
        delV = telV1 + (delV * del1 / DEL)
        delV = Vrefhab - delV
        IF delV < 1000000 THEN LOCATE 22, 69: PRINT USING "#######"; delV;
     
6051    TELdist = SQR(((x - x1) ^ 2) + ((y - y1) ^ 2))
        IF TELdist < 1000000 THEN LOCATE 21, 69: PRINT USING "####.###"; TELdist / 1000;
6052    RETURN

6060    telX1 = telX2
        telY1 = telY2
        telV1 = telV2
        IF EOF(2) THEN 6070
        INPUT #2, telX2
        IF EOF(2) THEN 6070
        INPUT #2, telY2
        IF EOF(2) THEN 6070
        INPUT #2, telV2
        GOTO 6053

6070    CLOSE #2
        telTRACK = 0
        LOCATE 21, 59: PRINT "                     ";
        LOCATE 22, 59: PRINT "                     ";
        RETURN
      

        'Start track recording
6100    IF TELEflag = 1 THEN 6110
        TELEflag = 1
        telTRACK = 0
        CLOSE #2
        TELEbk = TIMER
6101    LOCATE 9, 60: PRINT "8 charaters a-z 0-9";
        LOCATE 10, 60: PRINT "Save File: "; : INPUT ; "", filename$
        IF filename$ = "" THEN TELEflag = 0: GOTO 6120
        OPEN "R", #2, filename$
        IF LOF(2) < 1 THEN CLOSE #2: GOTO 6105
        CLOSE #2
        LOCATE 11, 60: PRINT "File exists";
        LOCATE 12, 60: PRINT "overwrite? "; : INPUT ; "", z$
        IF UCASE$(LEFT$(z$, 1)) = "Y" THEN 6105
        FOR i = 9 TO 12
         LOCATE i, 60: PRINT "                  ";
        NEXT i
        GOTO 6101
6105    OPEN "O", #2, filename$
        CLS : GOSUB 405
        GOTO 6120
6110    TELEflag = 0
        CLOSE #2
6120    RETURN





'8000    FOR i = 1 TO 3021
'         IF ABS(300 + (Pz(i, 1) - cenX) * mag / AU) > 1000 THEN 8001
'         IF ABS(220 + (Pz(i, 2) - cenY) * mag / AU) > 1000 THEN 8001
'         PSET (300 + (Pz(i, 1) - cenX) * mag / AU, 220 + (Pz(i, 2) - cenY) * mag * 1 / AU), Pz(i, 0)
'8001    NEXT i
'        RETURN




9000    LOCATE 1, 30
        'IF ERL = 800 OR ERL = 801 THEN RESUME 803
        IF ERL = 91 THEN CLOSE #1: CLS : PRINT "'stars' file is missing or incomplete"
        'IF ERL = 80 THEN CLOSE #1: RESUME 97
        'IF ERL = 52 THEN CLOSE #1: CLS : RESUME 97
        'IF ERL = 801 THEN CLOSE #1: LOCATE 2, 35: PRINT "Telemetry failed"; : RESUME 804
        'IF ERL = 98 AND ERR = 76 THEN CLS : LOCATE 15, 5: PRINT "'"; Zpath$; "' Path not found"; : RESUME 97
        'IF ERL = 98 AND ERR = 53 THEN CLS : LOCATE 15, 5: PRINT "Backup file not found in '"; Zpath$; "'"; : RESUME 97
        PRINT ERR, ERL
        z$ = INPUT$(1)
        END

