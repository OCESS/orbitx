        DEFDBL A-Z
        DIM P(40, 11), Px(40, 5), Py(40, 5), Vx(40), Vy(40), b(1, 250), Ztel(50), nme$(40), clr(4), switch(60, 5)
        ON ERROR GOTO 5000
        locate 1,1,0
        CLS
        OPEN "R", #2, "OSBACKUP.RND", 8
        inpSTR$=space$(8)
        GET #2, 1, inpSTR$
        inpFLAG$=mid$(inpSTR$, 2, 5)
        outSTR$ = left$(inpSTR$,1)+"ORBIT5S"
        PUT #2, 1, outSTR$
        CLOSE #2

        clr(0) = 10
        clr(1) = 11
        clr(2) = 14
        clr(3) = 13
        clr(4) = 12
        IF inpFLAG$ = "XXXXX" THEN zpath$ = "": GOTO 98
97      LOCATE 5, 5
        PRINT "Telemetry Monitoring Utility for ORBIT v. 5O"
        INPUT ; "    path to main program: ", zpath$
        IF UCASE$(zpath$) = "QUIT" THEN END
98      CLS

        'Initialization Parameters
        'Radius P(i,5) and Mass P(i,4) of solar system objects
        OPEN "I", #1, "starsr"
        FOR i = 1 TO 3021
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
        NEXT i
        FOR i = 1 TO 241
         INPUT #1, z
         INPUT #1, z
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
         INPUT #1, nme$(i)
        NEXT i
        nme$(40) = "TARGET"
        CLOSE #1
        AU = 149597890000#
        RAD = 57.295779515#
        G = 6.673E-11
        Px(0, 3) = 0
        Py(0, 3) = 0
        Vx(0) = 0
        Vy(0) = 0
        P(0, 1) = 0
        P(0, 2) = 0
        GOSUB 800
        GOSUB 400
        tt = TIMER

        'MAIN PROGRAM
1       z$ = INKEY$
        IF z$ = CHR$(13) THEN RUN "engMCv"
        'IF AUTOdestruct = 1 THEN DESTRUCTcode$ = DESTRUCTcode$ + z$
        'IF LEN(DESTRUCTcode$) > 13 THEN AUTOdestruct = 0: DESTRUCTcode$ = ""
        'IF z$ = CHR$(0) + ";" THEN AUTOdestruct = 1 - ABS(AUTOdestruct): DESTRUCTcode$ = ""
        IF z$ = CHR$(27) THEN END
        COLOR 7, 0
        z$ = UCASE$(z$)
        IF z$ < "0" OR z$ > "X" THEN 2
        IF z$ = "T" AND MODULEflag = 0 THEN 2
        IF z$ = "W" THEN 2
        IF z$ = "V" THEN 2
        alt = ASC(z$) - 48
2       IF TIMER - tt >= 1 THEN GOSUB 800: GOSUB 300: gosub 400: tt = TIMER
        'LOCATE 2, 1
        'IF AUTOdestruct = 1 THEN COLOR 12, 0: PRINT "DESTRUCT CODE"; : COLOR 15, 0 ELSE PRINT "             ";
        'LOCATE 3, 1
        'IF AUTOdestruct = 0 THEN PRINT "             ";
        'IF AUTOdestruct = 1 THEN COLOR 12, 0: PRINT STRING$(LEN(DESTRUCTcode$), 42); STRING$(LEN(destruct$) - LEN(DESTRUCTcode$), 219);
        GOTO 1


        'SUBROUTINE: Calculate orbit parameters
        'Calculate gravitaional attraction to reference object
300     difx = Px(28, 3) - Px(ref, 3)
        dify = Py(28, 3) - Py(ref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        A = G * P(ref, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Vref = SQR(G * P(ref, 4) / R)
        Aref = angle
        Dref = R
        ACCref = A
        
        'Calculate gravitational attraction to target object
        difx = Px(28, 3) - Px(targ, 3)
        dify = Py(28, 3) - Py(targ, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF R < .1 THEN R = .1
        A = G * P(targ, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Vtarg = SQR(G * P(targ, 4) / R)
        Atarg = angle
        Dtarg = R
        ACCtarg = A
       
        VVx = Vx(targ) - Vx(28)
        VVy = Vy(targ) - Vy(28)
        IF VVy = 0 THEN IF VVx < 0 THEN Vvangle = .5 * 3.1415926535# ELSE Vvangle = 1.5 * 3.1415926535# ELSE Vvangle = ATN(VVx / VVy)
        IF VVy > 0 THEN Vvangle = Vvangle + 3.1415926535#
        IF Vvangle < 0 THEN Vvangle = Vvangle + 6.283185
        VangleDIFF = Atarg - Vvangle


        'Calculate gravitational attraction to alternate object
        difx = Px(28, 3) - Px(alt, 3)
        dify = Py(28, 3) - Py(alt, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF R = 0 THEN A = 0 ELSE A = G * P(targ, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        IF R = 0 THEN Valt = 0 ELSE Valt = SQR(G * P(targ, 4) / R)
        Aalt = angle
        Dalt = R
        ACCalt = A

        VVx = Vx(alt) - Vx(28)
        VVy = Vy(alt) - Vy(28)
        IF VVy = 0 THEN IF VVx < 0 THEN Vvangle = .5 * 3.1415926535# ELSE Vvangle = 1.5 * 3.1415926535# ELSE Vvangle = ATN(VVx / VVy)
        IF VVy > 0 THEN Vvangle = Vvangle + 3.1415926535#
        IF Vvangle < 0 THEN Vvangle = Vvangle + 6.283185
        VangleDIFF1 = Aalt - Vvangle


      
        'Calculate reference velocities
        Vhab = SQR(Vx(28) ^ 2 + Vy(28) ^ 2)
        Vrefhab = SQR((Vx(28) - Vx(ref)) ^ 2 + (Vy(28) - Vy(ref)) ^ 2)
        Vtarghab = SQR((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)
        Valthab = SQR((Vx(28) - Vx(alt)) ^ 2 + (Vy(28) - Vy(alt)) ^ 2)
        AtoTARG = ACCtarg
        IF COS(VangleDIFF) <> 0 AND Dtarg - P(targ, 5) <> 0 THEN AtoTARG = AtoTARG + ((((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2) / (2 * (Dtarg - P(targ, 5)))) * COS(VangleDIFF))
        VcenTARG = SQR(((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)) * -1 * COS(VangleDIFF)
        VtanTARG = SQR(((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)) * ABS(SIN(VangleDIFF))
        AtoALT = ACCalt
        IF COS(VangleDIFF1) <> 0 AND Dalt - P(alt, 5) <> 0 THEN AtoALT = AtoALT + ((((Vx(28) - Vx(alt)) ^ 2 + (Vy(28) - Vy(alt)) ^ 2) / (2 * (Dalt - P(alt, 5)))) * COS(VangleDIFF1))
        VcenALT = SQR(((Vx(28) - Vx(alt)) ^ 2 + (Vy(28) - Vy(alt)) ^ 2)) * -1 * COS(VangleDIFF1)
        VtanALT = SQR(((Vx(28) - Vx(alt)) ^ 2 + (Vy(28) - Vy(alt)) ^ 2)) * ABS(SIN(VangleDIFF1))

        IF Sangle < 0 THEN Sangle = 6.2831852# + Sangle
       
        difx = Px(alt, 3) - Px(targ, 3)
        dify = Py(alt, 3) - Py(targ, 3)
        DaltTARG = SQR((dify ^ 2) + (difx ^ 2)) - P(alt, 5) - P(targ, 5)
        difx = Px(alt, 3) - Px(ref, 3)
        dify = Py(alt, 3) - Py(ref, 3)
        DaltREF = SQR((dify ^ 2) + (difx ^ 2)) - P(alt, 5) - P(ref, 5)
       
        'Calculate angle from target to reference object
        difx = Px(targ, 3) - Px(ref, 3)
        dify = Py(targ, 3) - Py(ref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        atrh = ABS(angle - Aref)
        IF atrh > 3.1415926353# THEN atrh = ABS(atrh - 6.283185307#)
        IF targ = ref THEN atrh = 0
        RETURN



        'SUBROUTINE: Write telemetry data to screen
400     GOSUB 300
        IF master = 0 THEN COLOR 10, 1 ELSE COLOR 12, 4: BEEP
        LOCATE 5, 1: PRINT "MASTER ALARM";
        COLOR 0, 0
        IF HABexp > 0 THEN COLOR 6
        IF HABexp = 12 THEN COLOR 12
        LOCATE 6, 1: PRINT "HAB EXPLOSION";
        COLOR 0, 0
        IF AYSEexp > 0 THEN COLOR 6
        IF AYSEexp = 12 THEN COLOR 12
        LOCATE 7, 1: PRINT "AYSE EXPLOSION";
        COLOR 15, 0
        COLOR 11: LOCATE 1, 25: PRINT "              REFERENCE          TARGET       ALTERNATE";
        COLOR 13
        LOCATE 2, 20: PRINT TAB(40); nme$(ref); TAB(56); nme$(targ); TAB(72); nme$(alt);
        COLOR 11: LOCATE 3, 25: PRINT "DISTANCE: ";
        COLOR 15
        Dref = Dref - P(ref, 5) - P(28, 5)
        Dtarg = Dtarg - P(targ, 5) - P(28, 5)
        Dalt = Dalt - P(alt, 5) - P(28, 5)
        PRINT TAB(35); : IF Dref > 99999999999# THEN PRINT USING "#.#######^^^^"; Dref / 1000;  ELSE PRINT USING "##,###,###.##"; Dref / 1000;
        PRINT TAB(50); : IF Dtarg > 99999999999# THEN PRINT USING "##.#######^^^^"; Dtarg / 1000;  ELSE PRINT USING "###,###,###.##"; Dtarg / 1000;
        PRINT TAB(66); : IF Dalt > 99999999999# THEN PRINT USING "##.#######^^^^"; Dalt / 1000;  ELSE PRINT USING "###,###,###.##"; Dalt / 1000;
        COLOR 11: LOCATE 4, 25: PRINT "VELOCITY: ";
        COLOR 15
        PRINT TAB(35); : IF Vrefhab > 99999999999# THEN PRINT USING "#.#######^^^^"; Vrefhab / 1000;  ELSE PRINT USING "##,###,###.##"; Vrefhab / 1000;
        PRINT TAB(50); : IF Vtarghab > 99999999999# THEN PRINT USING "##.#######^^^^"; Vtarghab / 1000;  ELSE PRINT USING "###,###,###.##"; Vtarghab / 1000;
        PRINT TAB(66); : IF Valthab > 99999999999# THEN PRINT USING "##.#######^^^^"; Vlathab / 1000;  ELSE PRINT USING "###,###,###.##"; Valthab / 1000;
        COLOR 11: LOCATE 5, 28: PRINT "  CEN:";
        COLOR 15
        PRINT TAB(50); : IF VcenTARG > 99999999999# THEN PRINT USING "##.#######^^^^"; VcenTARG / 1000;  ELSE PRINT USING "###,###,###.##"; VcenTARG / 1000;
        PRINT TAB(66); : IF VcenALT > 99999999999# THEN PRINT USING "##.#######^^^^"; VcenALT / 1000;  ELSE PRINT USING "###,###,###.##"; VcenALT / 1000;
        COLOR 11: LOCATE 6, 28: PRINT "  TAN:";
        COLOR 15
        PRINT TAB(50); : IF VtanTARG > 99999999999# THEN PRINT USING "##.#######^^^^"; VtanTARG / 1000;  ELSE PRINT USING "###,###,###.##"; VtanTARG / 1000;
        PRINT TAB(66); : IF VtanALT > 99999999999# THEN PRINT USING "##.#######^^^^"; VtanALT / 1000;  ELSE PRINT USING "###,###,###.##"; VtanALT / 1000;
        COLOR 11: LOCATE 7, 25: PRINT "ANGLE:    ";
        COLOR 15
        PRINT TAB(42); : PRINT USING "###.##"; Aref * RAD;
        COLOR 11: PRINT TAB(49); "("; : COLOR 15: PRINT USING "###.##"; atrh * RAD; : COLOR 11: PRINT ")"; : COLOR 15
        PRINT TAB(58); : PRINT USING "###.##"; Atarg * RAD;
        PRINT TAB(74); : PRINT USING "###.##"; Aalt * RAD;
        COLOR 11: LOCATE 8, 25: PRINT "STOP ACC:  ";
        COLOR 15
        PRINT TAB(50); : IF AtoTARG > 999999999# THEN PRINT USING "##.#######^^^^"; AtoTARG;  ELSE PRINT USING "###,###,###.##"; AtoTARG;
        PRINT TAB(66); : IF AtoALT > 999999999# THEN PRINT USING "##.#######^^^^"; AtoALT;  ELSE PRINT USING "###,###,###.##"; AtoALT;
       
        IF AYSE = 150 THEN Hmass = fuel + AYSEfuel + 20275000 ELSE Hmass = fuel + 275000
        Haccel = (ENGforce * eng) / Hmass
        COLOR 11: LOCATE 9, 25: PRINT "ENGINE:   "; : COLOR 15: PRINT USING "####.#"; eng;
        IF AYSE = 150 THEN NORMALengineMAX = 640000 ELSE NORMALengineMAX = 437.5
        PRINT USING "####"; ENGINEforceMAX / NORMALengineMAX; : COLOR 11, 0: PRINT "%n";
        COLOR 11: LOCATE 10, 25: PRINT "ACCEL:    "; : COLOR 15: PRINT USING "####.###"; Haccel;
        COLOR 11: LOCATE 11, 25: PRINT "DRAG ACC: "; : COLOR 15: PRINT USING "####.###"; Are;
        COLOR 11: LOCATE 12, 25: PRINT "H fuel:   "; : COLOR 15: PRINT USING "########"; fuel;
        COLOR 11: LOCATE 13, 25: PRINT "A fuel:   "; : COLOR 15: PRINT USING "########"; AYSEfuel;
        COLOR 11: LOCATE 9, 49: PRINT "HEADING:"; : COLOR 15: PRINT USING "####.##"; Sangle * RAD;
        COLOR 11: LOCATE 10, 50: PRINT "COURSE:"; : COLOR 15: PRINT USING "####.##"; Vvangle * RAD;
        COLOR 11: LOCATE 12, 52: PRINT "RCSP:"; : COLOR 15: PRINT USING "####"; vernP!;
        COLOR 11: LOCATE 9, 66: PRINT "Dist. to REF";
        IF alt = ref THEN DaltREF = 0
        COLOR 15: LOCATE 10, 66: IF DaltREF > 99999999999# THEN PRINT USING "##.#######^^^^"; DaltREF / 1000;  ELSE PRINT USING "###,###,###.##"; (DaltREF) / 1000;
        COLOR 11: LOCATE 11, 66: PRINT "         TARG";
        IF alt = targ THEN DaltTARG = 0
        COLOR 15: LOCATE 12, 66: IF DaltTARG > 99999999999# THEN PRINT USING "##.#######^^^^"; DaltTARG / 1000;  ELSE PRINT USING "###,###,###.##"; (DaltTARG) / 1000;
        COLOR 11: LOCATE 14, 25: PRINT "NAV MODE: ";
        COLOR 15, 0
        IF NAVmode = 1 THEN COLOR 15, 12
          IF Sflag = 0 THEN PRINT "ccw prograde  "; : GOTO 401
          IF Sflag = 4 THEN PRINT "ccw retrograde"; : GOTO 401
          IF Sflag = 1 THEN PRINT "manual        "; : GOTO 401
          IF Sflag = 2 THEN PRINT "approach targ "; : GOTO 401
          IF Sflag = 5 THEN PRINT "pro Vtrg      "; : GOTO 401
          IF Sflag = 6 THEN PRINT "retr Vtrg     "; : GOTO 401
          IF Sflag = 3 THEN PRINT "depart ref    ";
401     COLOR 11, 0: LOCATE 15, 25: PRINT "TIME:     "; : COLOR 15: PRINT USING "####:"; year; : LOCATE 15, 40: PRINT USING "###:"; day; : LOCATE 15, 44: PRINT USING "##:"; hr; min; : LOCATE 15, 50: PRINT USING "##"; sec;
        COLOR 11: LOCATE 16, 25: PRINT "F rate:     "; : COLOR 15: PRINT USING "##.##"; ts;
        LOCATE 18, 1: COLOR 9, 0: PRINT "0-U"; : COLOR 11, 0: PRINT "   Select Alt";
        LOCATE 19, 1: COLOR 9, 0: PRINT "enter"; : COLOR 11, 0: PRINT " Power Grid";
        'LOCATE 20, 1: COLOR 9, 0: PRINT "F1"; : COLOR 11, 0: PRINT "    DESTRUCT";
        COLOR 8 + (6 * para): LOCATE 11, 19: PRINT "CHUTE";
        COLOR 8 + (6 * SRB): LOCATE 9, 21: PRINT "SRB";
        COLOR 11, 0: LOCATE 13, 49: PRINT "DENSITY: "; : COLOR 15, 0: PRINT USING "###.##"; Pr;
        COLOR 11, 0: LOCATE 14, 52: PRINT "WIND:"; : COLOR 15, 0: PRINT USING "####"; Wsp; : COLOR 11, 0: PRINT " m/s "; ': COLOR 15, 0: PRINT Wdr$;
        LOCATE 13, 1: COLOR 11, 0: PRINT "AYSE DRIVE"
        LOCATE 14, 1
        IF AYSE = 150 THEN COLOR 10, 0: PRINT "DOCKED  ";  ELSE COLOR 8, 0: PRINT "UNDOCKED";
        'IF AYSE <> 150 AND AYSEad > 0 THEN COLOR 11, 0 ELSE COLOR 8, 0
        'LOCATE 15, 1: PRINT "AUTODOCKING";
        LOCATE 15, 1
        IF AYSEdl > 0 THEN COLOR 10, 0 ELSE COLOR 8, 0
        PRINT "DOCKING LATCH";
        RETURN


        'SUBROUTINE: Timed telemetry retrieval
800     k=1
        color 10, 0: locate 2,1:print "FLIGHT TELEM";
801     OPEN "R", #1, "OSBACKUP.RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1427 then color 12,0:locate 2,1:print "FLIGHT TELEM";:goto 830
        ORBITversion$=mid$(inpSTR$,2,7)
        IF left$(ORBITversion$,5) = "XXXXX" THEN RUN "orbit5vt"
        if ORBITversion$<>"ORBIT5S" then color 12,0:locate 2,1:print "FLIGHT TELEM";:goto 830
        if chkCHAR1$=chkCHAR2$ then 802
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        k=k+1
        if k<3 then 801
        color 12,0:locate 2,1:print "FLIGHT TELEM";
        goto 830

802     if FLIGHTchkCHAR$ = chkCHAR1$ then color 14, 0:locate 2, 1: print "FLIGHT TELEM"; else FLIGHTchkCHAR$ = chkCHAR1$
        k=2+15
        eng = cvs(mid$(inpSTR$,k,4)):k=k+4
        vflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Aflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Sflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Are = cvd(mid$(inpSTR$,k,8)):k=k+16
        'mag = cvd(mid$(inpSTR$,k,8)):k=k+8
        Sangle = cvd(mid$(inpSTR$,k,4)):k=k+6
        'cen = cvi(mid$(inpSTR$,k,2)):k=k+2
        targ = cvi(mid$(inpSTR$,k,2)):k=k+2
        ref = cvi(mid$(inpSTR$,k,2)):k=k+4
        'trail=cvi(mid$(inpSTR$,k,2)):k=k+2
        Cdh = cvs(mid$(inpSTR$,k,4)):k=k+4
        if Cdh>.003 then para=1 else para=0
        SRB = cvs(mid$(inpSTR$,k,4)):k=k+6
        'tr = cvi(mid$(inpSTR$,k,2)):k=k+2
        dte = cvi(mid$(inpSTR$,k,2)):k=k+2
        ts = cvd(mid$(inpSTR$,k,8)):k=k+8
        OLDts = cvd(mid$(inpSTR$,k,8)):k=k+8
        vernP! = cvs(mid$(inpSTR$,k,4)):k=k+4
        Eflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        year = cvi(mid$(inpSTR$,k,2)):k=k+2
        day = cvi(mid$(inpSTR$,k,2)):k=k+2
        hr = cvi(mid$(inpSTR$,k,2)):k=k+2
        min = cvi(mid$(inpSTR$,k,2)):k=k+2
        sec = cvd(mid$(inpSTR$,k,8)):k=k+14
        'AYSEangle = cvs(mid$(inpSTR$,k,4)):k=k+4
        'AYSEscrape = cvi(mid$(inpSTR$,k,2)):k=k+2
        Wsp = cvs(mid$(inpSTR$,k,4)):k=k+4
        Wdir = cvs(mid$(inpSTR$,k,4)):k=k+14
        IF Wdir < 3 THEN Wdr$ = " CW"
        IF Wdir = 0 THEN Wdr$ = " IN"
        IF Wdir > 3 THEN Wdr$ = "OUT"
        IF Wdir > 4 THEN Wdr$ = "CCW"
        'HABrotate = cvs(mid$(inpSTR$,k,4)):k=k+4
        'AYSE = cvi(mid$(inpSTR$,k,2)):k=k+2
        'Ztel(9) = cvs(mid$(inpSTR$,k,4)):k=k+4
        MODULEflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        AYSEdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        OCESSdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        HABexp = cvi(mid$(inpSTR$,k,2)):k=k+2
        AYSEexp = cvi(mid$(inpSTR$,k,2)):k=k+2
        NAVfailFLAG = cvs(mid$(inpSTR$,k,4)):k=k+4
        ENGforce = cvs(mid$(inpSTR$,k,4)):k=k+4
        NAVfailure = cvl(mid$(inpSTR$,k,4)):k=k+8
        'Ztel(14) = cvs(mid$(inpSTR$,k,4)):k=k+4
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
        IF vernP! > 999 THEN vernP! = 999
        IF vernP! < 0 THEN vernP! = 0
        Ltx = (P(ref, 5) * SIN(LONGtarg))
        Lty = (P(ref, 5) * COS(LONGtarg))
        Px(40, 3) = Px(ref, 3) + Ltx
        Py(40, 3) = Py(ref, 3) + Lty
        Vx(40) = Vx(ref)
        Vy(40) = Vy(ref)


830     k=1
        color 10,0
        locate 3, 1:print "ENG TELEM";
833     OPEN "R", #1, "ORBITSSE.RND", 1159
        inpSTR$=space$(1159)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1159 then locate 3, 1:color 12,0:print "ENG TELEM";:goto 839
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 832
        k=k+1
        if k<3 then 833
        locate 3, 1:color 12,0:print "ENG TELEM";
        goto 839
        
832     if ENGchkCHAR$ = chkCHAR1$ then color 14, 0:locate 3, 1: print "ENG TELEM"; else ENGchkCHAR$ = chkCHAR1$
        k=2
        NAVmode=CVD(mid$(inpSTR$,k,8)):k=k+8
        ENGINEforceMAX=CVD(mid$(inpSTR$,k,8)):k=k+24
        'HABfuel#=CVD(mid$(inpSTR$,k,8)):k=k+8
        'AYSEfuel#=CVD(mid$(inpSTR$,k,8)):k=k+8
        
        HABexplosion=CVD(mid$(inpSTR$,k,8)):k=k+8
        AYSEexplosion=CVD(mid$(inpSTR$,k,8)):k=k+8
        module=CVD(mid$(inpSTR$,k,8)):k=k+8
        tsLIMIT=CVD(mid$(inpSTR$,k,8)):k=k+8
        RADmax=CVD(mid$(inpSTR$,k,8)):k=k+8
        zz=CVD(mid$(inpSTR$,k,8)):k=k+8 
        RSCPop = 1 AND zz
        AYSEad=CVD(mid$(inpSTR$,k,8)):k=k+8
        AYSEdl=CVD(mid$(inpSTR$,k,8)):k=k+8
        AYSE=CVD(mid$(inpSTR$,k,8)):k=k+8
        windCEN=CVD(mid$(inpSTR$,k,8)):k=k+8
        windACC=CVD(mid$(inpSTR$,k,8)):k=k+8
        windANG=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zufo=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zref=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zrefalt=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zangle=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zorient=CVD(mid$(inpSTR$,k,8)):k=k+8
        Zaccel=CVD(mid$(inpSTR$,k,8)):k=k+8
        Ztarg=CVD(mid$(inpSTR$,k,8)):k=k+8
        Rshield=CVD(mid$(inpSTR$,k,8)):k=k+8
        zz=CVD(mid$(inpSTR$,k,8)):k=k+8
        master=cint(CVD(mid$(inpSTR$,k,8))):k=k+8

        k = 211
        Is1=CVS(mid$(inpSTR$,k,4)):k=k+4
        Is2=CVS(mid$(inpSTR$,k,4)):k=k+4
        Is3=CVS(mid$(inpSTR$,k,4)):k=k+4
        Is4=CVS(mid$(inpSTR$,k,4)):k=k+4
        Is5=CVS(mid$(inpSTR$,k,4)):k=k+4
        Vbus1=CVS(mid$(inpSTR$,k,4)):k=k+4
        Vbus2=CVS(mid$(inpSTR$,k,4)):k=k+4
        Vbus3=CVS(mid$(inpSTR$,k,4)):k=k+4
        Vbus4=CVS(mid$(inpSTR$,k,4)):k=k+4
        Vbus5=CVS(mid$(inpSTR$,k,4)):k=k+4
        Ibus1=CVS(mid$(inpSTR$,k,4)):k=k+4
        Ibus2=CVS(mid$(inpSTR$,k,4)):k=k+4
        Ibus3=CVS(mid$(inpSTR$,k,4)):k=k+4
        Ibus4=CVS(mid$(inpSTR$,k,4)):k=k+4
        Ibus5=CVS(mid$(inpSTR$,k,4)):k=k+4
        Htemp = CVS(mid$(inpSTR$,273,4))
        FCtemp = CVS(mid$(inpSTR$,385,4))
        BATT1temp = CVS(mid$(inpSTR$,417,4))
        BATT3temp = CVS(mid$(inpSTR$,481,4))
        Atemp = CVS(mid$(inpSTR$,721,4))

891     COLOR 11, 0: LOCATE 18, 25: PRINT "BUS:"; : COLOR 14, 0: PRINT " VOLTS";
        LOCATE 19, 25: COLOR 11, 0: PRINT "  1:"; : COLOR 10, 0: PRINT USING "######"; Vbus1;
        LOCATE 20, 25: COLOR 11, 0: PRINT "  2:"; : COLOR 10, 0: PRINT USING "######"; Vbus2;
        LOCATE 21, 25: COLOR 11, 0: PRINT "  3:"; : COLOR 10, 0: PRINT USING "######"; Vbus3;
        LOCATE 22, 25: COLOR 11, 0: PRINT "  4:"; : COLOR 10, 0: PRINT USING "######"; Vbus4;
        COLOR 14, 0: LOCATE 18, 37: PRINT "CURRENT";
        LOCATE 19, 37: COLOR 10, 0: PRINT USING "#######"; Ibus1;
        LOCATE 20, 37: COLOR 10, 0: PRINT USING "#######"; Ibus2;
        LOCATE 21, 37: COLOR 10, 0: PRINT USING "#######"; Ibus3;
        LOCATE 22, 37: COLOR 10, 0: PRINT USING "#######"; Ibus4;
        LOCATE 18, 48: COLOR 11, 0: PRINT "SOURCE:"; : COLOR 14, 0: LOCATE 18, 56: PRINT "OUTPUT";
        LOCATE 19, 49: COLOR 11, 0: PRINT "H Rct:"; : COLOR 10, 0: PRINT USING "#######"; Is1;
        LOCATE 20, 49: COLOR 11, 0: PRINT "   FC:"; : COLOR 10, 0: PRINT USING "#######"; Is2;
        LOCATE 21, 49: COLOR 11, 0: PRINT " BAT1:"; : COLOR 10, 0: PRINT USING "#######"; Is3;
        LOCATE 23, 49: COLOR 11, 0: PRINT "A Rct:"; : COLOR 10, 0: PRINT USING "#######"; Is5;
        LOCATE 22, 49: COLOR 11, 0: PRINT " BAT3:"; : COLOR 10, 0: PRINT USING "#######"; Is4;
        COLOR 14, 0: LOCATE 18, 63: PRINT "TEMP";
        LOCATE 19, 63:  COLOR 10, 0: PRINT USING "####"; Htemp;
        LOCATE 20, 63:  COLOR 10, 0: PRINT USING "####"; FCtemp;
        LOCATE 21, 63:  COLOR 10, 0: PRINT USING "####"; BATT1temp;
        LOCATE 23, 63:  COLOR 10, 0: PRINT USING "####"; Atemp;
        LOCATE 22, 63:  COLOR 10, 0: PRINT USING "####"; BATT3temp;
839     RETURN


900     'IF AUTOdestruct = -1 THEN 902
        'OPEN "O", #2, zpath$ + "ORBITMC"
        'IF DESTRUCTcode$ <> destruct$ THEN PRINT #2, "*$&#@@##@": GOTO 901
        'IF DESTRUCTcode$ = destruct$ THEN PRINT #2, "*$&##@@#@"
        'COLOR 12, 0
        'LOCATE 3, 1
        'PRINT "TRANSMITTED  ";
        'AUTOdestruct = -1
        'DESTRUCTcode$ = ""
901     'CLOSE #2
902     RETURN


1000    DATA "     Sun"
        DATA " Mercury"
        DATA "   Venus"
        DATA "   Earth"
        DATA "    Mars"
        DATA " Jupiter"
        DATA "  Saturn"
        DATA "  Uranus"
        DATA " Neptune"
        DATA "   Pluto"
        DATA "    Moon"
        DATA "  Phobos"
        DATA "  Deimos"
        DATA "      Io"
        DATA "  Europa"
        DATA "Ganymede"
        DATA "Callisto"
        DATA "  Tethys"
        DATA "   Dione"
        DATA "    Rhea"
        DATA "   Titan"
        DATA " Iapatus"
        DATA "   Ariel"
        DATA " Umbriel"
        DATA " Titania"
        DATA "  Oberon"
        DATA "  Triton"
        DATA "  Charon"
        DATA " Habitat"
        DATA "   Ceres"
        DATA "Borrelly"
        DATA "   Vesta"
        DATA "    AYSE"
        DATA "   Sedna"
        DATA "  Quaoar"
        DATA "     ISS"
        DATA "  MODULE"
        DATA "   OCESS"
        DATA "    UFO1"
        DATA "    UFO2"
        DATA "  TARGET"


5000    'IF ERL = 800 OR ERL = 801 THEN tt = TIMER + .5: RESUME 803
        'IF ERL = 900 THEN tt = TIMER + .5: RESUME 901
        'IF ERL = 98 AND ERR = 76 THEN CLS : LOCATE 15, 5: PRINT "'"; zpath$; "' Path not found"; : RESUME 97
        'IF ERL = 98 AND ERR = 53 THEN CLS : LOCATE 15, 5: PRINT "Backup file not found in '"; zpath$; "'"; : RESUME 97
        'IF ERL = 830 THEN 5100
        LOCATE 1, 30: PRINT "unknown error: "; ERR; ERL
        z$ = INPUT$(1)
        END

5100    'tUP = TIMER
5101    'IF TIMER - tUP < .1 THEN 5101
        'CLOSE #1
        'RESUME 830


6000    'OPEN "R", #1, "OSBACKUP", 7
        'FIELD #1, 7 AS aOS$
        'LSET aOS$ = "ORBIT5S"
        'CLOSE #1
        'RUN "telem"

