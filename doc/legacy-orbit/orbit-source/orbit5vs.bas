        DEFDBL A-Z
        DIM P(40, 11), Px(40, 5), Py(40, 5), Vx(40), Vy(40), B(1, 250), Ztel(50), nme$(48), clr(8), clrr(4)
        DIM DEVICEs(75), SOURCEs(5, 30), SHORT(5), SWITCHs%(70), malfNAME$(40), devKEY(70), switchlist(100, 6), switchlist$(60, 1), malf(40, 2)
        ON ERROR GOTO 5000
        PALETTE 6, 5
        CLS
97      LOCATE 5, 5, 0
        OPEN "R", #2, "OSBACKUP", 8
        inpSTR$=space$(8)
        GET #2, 1, inpSTR$
        inpFLAG$=right$(inpSTR$,7)
        outSTR$ = left$(inpSTR$,1)+"ORBIT5S"
        PUT #2, 1, outSTR$
        CLOSE #2

        filename$="orb5rEs"
        Zpath$=""
        IF inpFLAG$ = "XXXXXYY" THEN filename$="engsimrs": goto 51
        IF inpFLAG$ = "XXXXXXX" THEN GOTO 51

        PRINT "Simulation Error Activation Utility for ORBIT v. 5t"
        PRINT
        INPUT ; "    path to main program: ", zpath$
        IF UCASE$(zpath$) = "QUIT" THEN END

51      clr(0) = 10
        clr(1) = 11
        clr(2) = 14
        clr(3) = 13
        clr(4) = 12
        clrr(0) = 10
        clrr(1) = 6
        clrr(2) = 12
        WINDref = -1
        SOURCEs(1, 4) = 10000
        SOURCEs(2, 4) = 120
        SOURCEs(3, 4) = 120
        SOURCEs(4, 4) = 100000
        SOURCEs(5, 4) = 100000
        SOURCEs(0, 1) = 1
        SOURCEs(0, 2) = 1
        CLS
        COLOR 9, 0
        LOCATE 1, 18: PRINT "ENTER";
        COLOR 10, 0
        LOCATE 1, 24: PRINT "UPDATED";
        COLOR 7, 0


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
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        CLOSE #1
        nme$(40) = "TARGET"
        nme$(41) = "  progrd"
        nme$(42) = "retrogrd"
        nme$(43) = " deptarg"
        nme$(44) = " apptarg"
        nme$(45) = " proVtrg"
        nme$(46) = " retVtrg"
        RESTORE 4390
        FOR i = 1 TO 35
         READ malfNAME$(i), malf(i, 1), malf(i, 2)
        NEXT i
        RESTORE 6000
        FOR i = 1 TO 52
         READ x1, y1, z1, switchlist$(i, 0), switchlist$(i, 1), switchlist(z1, 5)
         switchlist(i, 0) = ASC(switchlist$(i, 0)) - 31
         switchlist(i, 1) = x1
         switchlist(i, 2) = y1
         switchlist(i, 3) = z1
         switchlist(ASC(switchlist$(i, 0)) - 31, 4) = i
        NEXT i

        AUTOupdate = -1
        Zufo = 2
        Ztarg = 38
        Zorient = 0
        Zrefalt = 100000
        VUFO = 1
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
        GOSUB 830
        GOSUB 300
        GOSUB 400
        OPEN "R", #1, filename$+".RND", 412
        GOSUB 121
        tt = TIMER

        'MAIN PROGRAM
1       z$ = INKEY$
        IF z$ = CHR$(27) THEN END
        IF AUTOupdate > -1 THEN COLOR 12, 4: LOCATE 1, 24: PRINT "AUTO "; : PRINT USING "##"; AUTOupdate - TIMER;
        IF AUTOupdate - TIMER < 1 AND AUTOupdate > -1 THEN GOSUB 100
        IF z$ = CHR$(0) + "H" OR z$ = CHR$(0) + "P" OR z$ = CHR$(0) + "=" THEN 2
        IF (z$ = CHR$(0) + "K" OR z$ = CHR$(0) + "M") AND UFOflag = 0 THEN 2
        IF z$ <> "" THEN COLOR 12, 4: LOCATE 1, 24: PRINT "UPDATE"; : COLOR 7, 0: PRINT " ";
2       IF z$ = CHR$(13) AND DEVICEselect = 0 THEN GOSUB 100
        IF z$ = CHR$(13) AND DEVICEselect <> 0 THEN GOSUB 4500: DEVICEselect = 0
        IF z$ = CHR$(0) + "<" AND DEVICEselect <> 0 THEN GOSUB 4500: DEVICEselect = 0
       
        IF z$ = "" THEN 4
        if z$ <> "R" then 11 
        if (DEVICEs(43) and 1) = 0 then DEVICEs(43) = DEVICEs(43) + 1 else DEVICEs(43) = DEVICEs(43) - 1 
11      if z$ <> "S" then 12
        if (DEVICEs(43) and 2) = 0 then DEVICEs(43) = DEVICEs(43) + 2 else DEVICEs(43) = DEVICEs(43) - 2
12      if z$ <> "T" then 13
        if (DEVICEs(43) and 4) = 0 then DEVICEs(43) = DEVICEs(43) + 4 else DEVICEs(43) = DEVICEs(43) - 4
13      IF ASC(z$) < 48 OR ASC(z$) > 122 THEN 4
        IF ABS(ASC(z$) - 88.5) < 8 THEN 4
        IF ABS(ASC(z$) - 61) < 3.5 THEN 4
        IF UFOflag = 1 THEN 4
        IF DEVICEselect <> 0 THEN GOSUB 4500
        z2 = ASC(z$) - 31
        y = switchlist(z2, 4)
        z2 = switchlist(y, 3)
        IF z2 = 0 THEN 4
        DEVICEselect = z2: GOSUB 4400: mlf = 1
       
4       IF z$ = CHR$(0) + "<" THEN UFOflag = 1 - UFOflag: GOSUB 4000: GOSUB 300: GOSUB 400
        IF z$ = CHR$(0) + "=" THEN UFOdisp = 1 * (1 - SGN(UFOdisp))
        IF z$ = CHR$(0) + ">" THEN UFOdisp = 2 * (1 - SGN(UFOdisp))
        IF z$ = CHR$(0) + "?" THEN UFOdisp = 3 * (1 - SGN(UFOdisp))
        IF z$ = CHR$(0) + "C" THEN MSLflag = 1 - MSLflag
        IF ABS(Px(38, 3)) + ABS(Py(38, 3)) = 0 THEN UFOdisp = 0
        IF z$ = "[" AND WINDref > -1 THEN WINDref = WINDref - 1
        IF z$ = "]" AND WINDref < 31 THEN WINDref = WINDref + 1
        IF windACC >= 20 THEN DELwind = 10 ELSE DELwind = 1
        IF windACC <= 5 THEN DELwind = .1
        IF z$ = "{" AND windACC > .1 THEN windACC = windACC - DELwind
        IF z$ = "}" THEN windACC = windACC + DELwind
        IF z$ = "\" THEN WINDangle = WINDangle + 90
        IF WINDangle > 280 THEN WINDangle = 0
        IF WINDref = -1 THEN windACC = 0: WINDangle = 0
        IF ABS(HABfuelleak) > .99 THEN habFUELdel = 1 ELSE habFUELdel = .01
        IF ABS(HABfuelleak) > 9 THEN habFUELdel = 10
        IF z$ = "," THEN HABfuelleak = HABfuelleak - habFUELdel
        IF z$ = "." THEN HABfuelleak = HABfuelleak + habFUELdel
        IF ABS(HABfuelleak) > 9990 THEN HABfuelleak = SGN(HABfuelleak) * 9990
        IF ABS(HABfuelleak) < .01 THEN HABfuelleak = 0
        IF ABS(AYSEfuelleak) > .99 THEN AYSEFUELdel = 1 ELSE AYSEFUELdel = .01
        IF ABS(AYSEfuelleak) > 9 THEN AYSEFUELdel = 10
        IF z$ = "<" THEN AYSEfuelleak = AYSEfuelleak - AYSEFUELdel
        IF z$ = ">" THEN AYSEfuelleak = AYSEfuelleak + AYSEFUELdel
        IF ABS(AYSEfuelleak) > 9990 THEN AYSEfuelleak = SGN(AYSEfuelleak) * 9990
        IF ABS(AYSEfuelleak) < .01 THEN AYSEfuelleak = 0
        IF z$ = CHR$(0) + ";" THEN master = 1 - master
        IF z$ = "*" THEN tsLIM = 1 - tsLIM
        IF z$ = "/" THEN EXPsup = EXPsup + 1: IF EXPsup > 3 THEN EXPsup = 0
        IF z$ = CHR$(0) + "D" THEN GOSUB 140
        IF z$ = CHR$(0) + CHR$(134) THEN RUN "orbit5vms"
        IF z$ = CHR$(0) + CHR$(133) THEN RUN "engSIMv"
       
        IF UFOflag + DEVICEselect = 0 THEN GOSUB 80
        IF UFOflag = 1 THEN GOSUB 81
        IF DEVICEselect > 0 THEN GOSUB 82


5       LOCATE 1, 1: COLOR 9, 0: PRINT "F1"; : COLOR 10 + (master * 2): PRINT " MASTER ALARM";
        FOR i = 1 TO 52
         LOCATE switchlist(i, 1), switchlist(i, 2)
         IF DEVICEselect = switchlist(i, 3) THEN clrbk = 1 ELSE clrbk = 0
         COLOR 9, clrbk
         PRINT switchlist$(i, 0);
         clrfg = 10
         GOSUB 4200
         'IF SWITCHs%(switchlist(i, 3)) > 0 THEN clrfg = 12
         'COLOR clrr(DEVICEs(switchlist(i, 3))), clrbk
         COLOR clrfg, clrbk
         PRINT switchlist$(i, 1);
         if i = 38 then color 9+((DEVICEs(43) and 1)*5),clrbk: print "R";
         if i = 39 then color 9+((DEVICEs(43) and 2)/2*5),clrbk: print "S";
         if i = 51 then color 9+((DEVICEs(43) and 4)/4*5),clrbk: print "T";
        NEXT i

        LOCATE 14, 67: COLOR 9, 0: PRINT "*"; : COLOR 8 + (4 * tsLIM), 0: PRINT "TS limit";
        LOCATE 15, 67: COLOR 9, 0: PRINT "/"; : COLOR 11, 0: PRINT "No Expl: ";
        COLOR 8 + (2 * (1 AND EXPsup)), 0: PRINT "H";
        COLOR 8 + (2 AND EXPsup), 0: PRINT "A";
        LOCATE 16, 1: COLOR 11, 0: PRINT "Wind source:"; : COLOR 9, 0: PRINT " []";
        LOCATE 17, 1: COLOR 11, 0: PRINT "      speed:"; : COLOR 9, 0: PRINT " {}"; : COLOR 11, 0: LOCATE 17, 26: PRINT "m/s";
        LOCATE 18, 1: COLOR 11, 0: PRINT "      angle:"; : COLOR 9, 0: PRINT " \";
        COLOR 14, 0
        LOCATE 16, 17: IF WINDref = -1 THEN PRINT "     OFF";  ELSE PRINT nme$(WINDref);
        LOCATE 17, 19: PRINT USING "####.#"; windACC;
        LOCATE 18, 20
        IF WINDangle = 0 THEN PRINT "   IN";
        IF WINDangle = 180 THEN PRINT "  OUT";
        IF WINDangle = 90 THEN PRINT "RIGHT";
        IF WINDangle = 270 THEN PRINT " LEFT";
        LOCATE 12, 54: IF HABfuelleak < 0 THEN PRINT "+";  ELSE PRINT "-";
        PRINT USING "####.##"; ABS(HABfuelleak); : COLOR 9: PRINT " ,."; : COLOR 14, 0
        LOCATE 13, 54: IF AYSEfuelleak < 0 THEN PRINT "+";  ELSE PRINT "-";
        PRINT USING "####.##"; ABS(AYSEfuelleak); : COLOR 9: PRINT " <>";
        COLOR 9, 0
        LOCATE 25, 1
        IF UFOflag + DEVICEselect = 0 THEN PRINT "arrows + -";  ELSE PRINT "          ";
        LOCATE 17, 35: COLOR 9, 0: PRINT "F10"; : COLOR 11, 0: PRINT " Clear Codes";
        LOCATE 18, 35: COLOR 9, 0: PRINT "F11"; : COLOR 11, 0: PRINT " Power Grid ";
        LOCATE 18, 53: COLOR 9, 0: PRINT "F12"; : COLOR 11, 0: PRINT " Telemetry  ";

        IF UFOflag = 1 THEN GOSUB 50
        IF DEVICEselect > 0 THEN GOSUB 4300



7       COLOR 7, 0
        IF TIMER - tt >= 5 THEN tt = TIMER: GOSUB 800: GOSUB 830: GOSUB 300: GOSUB 400
        GOSUB 3000
        'locate 19,1': print DEVICEs(1);
        'for i=1 to 47
        ' clrX=10
        ' if i=10 or i=20 or i=30 or i=40 or i=50 or i=60 then clrX=14
        ' color clrX,0
        ' if DEVICEs(i)<>0 then print "*"; else print "-";
        'next i
       ' 
        'locate 19,1': print DEVICEs(1);
        'for i=1 to 64
        ' clrX=10
        ' if i=10 or i=20 or i=30 or i=40 or i=50 or i=60 then clrX=14
        ' color clrX,0
        ' if SWITCHs%(i)<>0 then print "*"; else print "-";
        'next i
        'locate 19, 70:print SWITCHs%(1);

        GOTO 1

        'DISPLAY UFO INFORMATION
50      LOCATE 17, 53: COLOR 9, 0: PRINT "F9 "; : COLOR 11, 0: PRINT " Reposition ";
        COLOR 11
        LOCATE 17, 70: PRINT "UFO:";
        LOCATE 18, 70: PRINT "REF:";
        LOCATE 19, 70: PRINT "TRG:";
        LOCATE 20, 70: PRINT "ALT:";
        LOCATE 22, 70: PRINT "ANG:";
        LOCATE 24, 70: PRINT "ACC:";
        LOCATE 25, 70: IF MSLflag = 0 THEN PRINT "MSL:";  ELSE PRINT "RPL:";
        IF VUFO = 1 THEN COLOR 10, 1 ELSE COLOR 10, 0
        LOCATE 17, 77: IF Zufo = 2 THEN PRINT "OFF";  ELSE PRINT " ON";
        IF VUFO = 2 THEN COLOR 10, 1 ELSE COLOR 10, 0
        zz$ = nme$(Zref)
        FOR j = 1 TO 8
         IF MID$(zz$, j, 1) <> " " THEN zz$ = MID$(zz$, j, 6): GOTO 57
        NEXT j
57      IF LEN(zz$) < 6 THEN zz$ = zz$ + SPACE$(6 - LEN(zz$))
        LOCATE 18, 74: PRINT zz$;
        IF VUFO = 3 THEN COLOR 10, 1 ELSE COLOR 10, 0
        zz$ = nme$(Ztrg)
        FOR j = 1 TO 8
         IF MID$(zz$, j, 1) <> " " THEN zz$ = MID$(zz$, j, 6): GOTO 58
        NEXT j
58      IF LEN(zz$) < 6 THEN zz$ = zz$ + SPACE$(6 - LEN(zz$))
        LOCATE 19, 74: PRINT zz$;
        COLOR 10
        LOCATE 21, 74: PRINT USING "####.#"; ZtrgAngle * RAD;
        IF VUFO = 4 THEN COLOR 10, 1 ELSE COLOR 10, 0
        LOCATE 20, 74: PRINT USING "#######"; Zrefalt / 1000;
        IF VUFO = 6 THEN COLOR 10, 1 ELSE COLOR 10, 0
        LOCATE 23, 72: PRINT nme$(Zorient + 41);
        IF VUFO = 5 THEN COLOR 10, 1 ELSE COLOR 10, 0
        LOCATE 22, 74: PRINT USING "####.#"; Zangle * RAD;
        IF VUFO = 7 THEN COLOR 10, 1 ELSE COLOR 10, 0
        LOCATE 24, 74: PRINT USING "######"; Zaccel;
        IF VUFO = 8 THEN COLOR 10, 1 ELSE COLOR 10, 0
        zz$ = nme$(Ztarg)
        FOR j = 1 TO 8
         IF MID$(zz$, j, 1) <> " " THEN zz$ = MID$(zz$, j, 6): GOTO 59
        NEXT j
59      IF LEN(zz$) < 6 THEN zz$ = zz$ + SPACE$(6 - LEN(zz$))
        LOCATE 25, 74
        IF Ztarg = 39 THEN PRINT "ABORT ";
        IF Ztarg = 38 THEN PRINT "OFF   ";
        IF Ztarg < 38 THEN PRINT zz$;
        RETURN


        'SOURCE & BUS MODIFICATIONS
80      IF z$ = CHR$(0) + "H" THEN SOURCEs(0, 1) = SOURCEs(0, 1) - 1
        IF z$ = CHR$(0) + "P" THEN SOURCEs(0, 1) = SOURCEs(0, 1) + 1
        IF z$ = CHR$(0) + "M" THEN SOURCEs(0, 2) = SOURCEs(0, 2) + 1
        IF z$ = CHR$(0) + "K" THEN SOURCEs(0, 2) = SOURCEs(0, 2) - 1
        IF SOURCEs(0, 1) > 5 THEN SOURCEs(0, 1) = 1
        IF SOURCEs(0, 1) < 1 THEN SOURCEs(0, 1) = 5
        IF SOURCEs(0, 2) > 4 THEN SOURCEs(0, 2) = 1
        IF SOURCEs(0, 2) < 1 THEN SOURCEs(0, 2) = 4

        IF ABS(SOURCEs(SOURCEs(0, 1), 1)) > 49 THEN incr = 10 ELSE incr = 1
        IF ABS(SOURCEs(SOURCEs(0, 1), 1)) > 490 THEN incr = 100
        IF SOURCEs(0, 2) = 1 AND z$ = "+" THEN SOURCEs(SOURCEs(0, 1), 1) = SOURCEs(SOURCEs(0, 1), 1) + incr
        IF SOURCEs(0, 2) = 1 AND z$ = "-" THEN SOURCEs(SOURCEs(0, 1), 1) = SOURCEs(SOURCEs(0, 1), 1) - incr: IF SOURCEs(SOURCEs(0, 1), 1) < -1 * SOURCEs(SOURCEs(0, 1), 4) THEN SOURCEs(SOURCEs(0, 1), 1) = -1 * SOURCEs(SOURCEs(0, 1), 4)
      
        IF SOURCEs(0, 2) = 2 AND z$ = "+" THEN SOURCEs(SOURCEs(0, 1), 2) = SOURCEs(SOURCEs(0, 1), 2) + 1
        IF SOURCEs(0, 2) = 2 AND z$ = "-" THEN SOURCEs(SOURCEs(0, 1), 2) = SOURCEs(SOURCEs(0, 1), 2) - 1: IF SOURCEs(SOURCEs(0, 1), 2) < 0 THEN SOURCEs(SOURCEs(0, 1), 2) = 0

        IF SOURCEs(0, 2) = 3 AND (z$ = "+" OR z$ = "-") THEN SOURCEs(SOURCEs(0, 1), 0) = 1 - SOURCEs(SOURCEs(0, 1), 0)
      
        IF SOURCEs(0, 2) = 4 AND z$ = "+" THEN SOURCEs(SOURCEs(0, 1), 3) = SOURCEs(SOURCEs(0, 1), 3) + 1: IF SOURCEs(SOURCEs(0, 1), 3) > 30 THEN SOURCEs(SOURCEs(0, 1), 3) = 30
        IF SOURCEs(0, 2) = 4 AND z$ = "-" THEN SOURCEs(SOURCEs(0, 1), 3) = SOURCEs(SOURCEs(0, 1), 3) - 1: IF SOURCEs(SOURCEs(0, 1), 3) < 0 THEN SOURCEs(SOURCEs(0, 1), 3) = 0
        RETURN


        'UFO CONTROLS
81      IF z$ = CHR$(0) + "H" THEN VUFO = VUFO - 1: IF VUFO = 0 THEN VUFO = 8
        IF z$ = CHR$(0) + "P" THEN VUFO = VUFO + 1: IF VUFO = 9 THEN VUFO = 1
        IF z$ = CHR$(0) + "M" THEN ON VUFO GOSUB 2000, 2010, 2070, 2020, 2060, 2030, 2040, 2050
        IF z$ = CHR$(0) + "K" THEN ON VUFO GOSUB 2000, 2110, 2170, 2120, 2160, 2130, 2140, 2150
        IF z$ = CHR$(0) + "R" THEN Ztarg = 38
        IF z$ = CHR$(0) + "S" THEN Ztarg = 39
        IF z$ = CHR$(0) + "O" THEN Ztarg = 28
        IF z$ = CHR$(0) + "Q" THEN Ztarg = 32
        IF z$ = CHR$(0) + "G" THEN Zref = 3
        IF z$ = CHR$(0) + "I" THEN Zref = 28
        RETURN


        'MODIFICATIONS TO SPECIFIC DEVICES
82      DEVmax = CINT(LOG((switchlist(DEVICEselect, 5))) * 1.4426955#) + 1
        IF z$ = CHR$(0) + "H" THEN mlf = mlf - 1: IF mlf = 0 THEN mlf = DEVmax
        IF z$ = CHR$(0) + "P" THEN mlf = mlf + 1: IF mlf > DEVmax THEN mlf = 1
        IF ((2 ^ (mlf - 1)) AND switchlist(DEVICEselect, 5)) = 0 THEN 82
        IF z$ = "+" THEN malf(mlf, 0) = malf(mlf, 0) + 1
        IF z$ = "-" THEN malf(mlf, 0) = malf(mlf, 0) - 1
        RETURN


        'SUBROUTINE: Save error codes to code file
100     SWITCHs%(53) = (4096 AND SWITCHs%(52)) / 4096
        DEVICEs(45) = tsLIM
        DEVICEs(46) = (1 AND EXPsup)
        DEVICEs(47) = (2 AND EXPsup) / 2
        SWITCHs%(17) = (3 AND SWITCHs%(15))
        SWITCHs%(24) = (12 AND SWITCHs%(15)) / 4
        SWITCHs%(25) = (12 AND SWITCHs%(15)) / 4

        chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$ = chr$(chkBYTE+64)
        FOR i = 1 TO 5
         outSTR$ = outSTR$ + mkd$(SOURCEs(i, 1))
         outSTR$ = outSTR$ + mkd$(SOURCEs(i, 2))
         outSTR$ = outSTR$ + mkd$(SOURCEs(i, 0))
        NEXT i
        FOR i = 1 TO 47
         outSTR$ = outSTR$ + mki$(DEVICEs(i))
        NEXT i
        FOR i = 1 TO 64
         IF i = 15 THEN outSTR$ = outSTR$ + mki$(SWITCHs%(17)) ELSE outSTR$ = outSTR$ + mki$(SWITCHs%(i))
        NEXT i
        FOR i = 1 TO 4
         IF SOURCEs(i, 3) > 0 THEN minVAL = 19 ELSE minVAL = 0
         outSTR$ = outSTR$ + mks$(25 - SOURCEs(i, 3) - minVAL)
        NEXT i
        outSTR$ = outSTR$ + mks$(HABfuelleak)
        outSTR$ = outSTR$ + mks$(AYSEfuelleak)
        IF WINDref > -1 THEN outSTR$ = outSTR$ + mks$(WINDref) ELSE outSTR$ = outSTR$ + mks$(0)
        outSTR$ = outSTR$ + mks$(windACC)
        outSTR$ = outSTR$ + mks$(WINDangle / RAD)
        outSTR$ = outSTR$ + mks$(Zufo)
        outSTR$ = outSTR$ + mks$(Zref)
        outSTR$ = outSTR$ + mks$(Zrefalt)
        outSTR$ = outSTR$ + mks$(Zangle)
        outSTR$ = outSTR$ + mks$(Zorient)
        outSTR$ = outSTR$ + mks$(Zaccel)
        outSTR$ = outSTR$ + mks$(Ztarg * (1 - (2 * MSLflag)))
        outSTR$ = outSTR$ + mks$(master)
        outSTR$ = outSTR$ + chr$(chkBYTE+64)
        open "R", #1, "orb5rEs.RND", 412
        put #1, 1, outSTR$
        CLOSE #1
        Beep
        COLOR 10, 1
        LOCATE 1, 24: PRINT "UPDATED";
        IF AUTOupdate > -1 THEN COLOR 10, 1: LOCATE 1, 24: PRINT "UPDATED"; : AUTOupdate = -1: Ztarg = 38: Zufo = 2: MSLflag = 0
        IF MSLflag = 1 THEN Ztarg = 38: Zufo = 2: MSLflag = 0: AUTOupdate = TIMER + 10
        COLOR 7, 0
110     RETURN


        'SUBROUTINE: Upload existing error codes from code file
120     OPEN "R", #1, "orb5rEs.RND", 412
121     inpSTR$=space$(412)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 412 then gosub 140: return
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$<>chkCHAR2$ then gosub 140: return
        k = 2
        FOR i = 1 TO 5
         SOURCEs(i, 1)=cvd(mid$(inpSTR$,k,8)):k=k+8
         SOURCEs(i, 2)=cvd(mid$(inpSTR$,k,8)):k=k+8
         SOURCEs(i, 0)=cvd(mid$(inpSTR$,k,8)):k=k+8
        NEXT i
        FOR i = 1 TO 47
         DEVICEs(i)=cvi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        tsLIM = DEVICEs(45)
        EXPsup = DEVICEs(46) + (2 * DEVICEs(47))
        FOR i = 1 TO 64
         SWITCHs%(i)=cvi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        SWITCHs%(15) = SWITCHs%(15) + (4 * SWITCHs%(24))
        SWITCHs%(52) = SWITCHs%(52) + (4096 * SWITCHs%(53))
        FOR i = 1 TO 4
         SOURCEs(i, 3)=cvs(mid$(inpSTR$,k,4)):k=k+4
         IF SOURCEs(i, 3) < 25 THEN minVAL = 19 ELSE minVAL = 0
         SOURCEs(i, 3) = 25 - SOURCEs(i, 3) - minVAL
        NEXT i
        HABfuelleak=cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEfuelleak=cvs(mid$(inpSTR$,k,4)):k=k+4
        WINDref=cvs(mid$(inpSTR$,k,4)):k=k+4
        IF WINDref = 0 THEN WINDref = -1
        windACC=cvs(mid$(inpSTR$,k,4)):k=k+4
        WINDangle=cvs(mid$(inpSTR$,k,4)):k=k+4
        WINDangle = WINDangle * RAD
        Zufo=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zref=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zrefalt=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zangle=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zorient=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zaccel=cvs(mid$(inpSTR$,k,4)):k=k+4
        Ztarg=cvs(mid$(inpSTR$,k,4)):k=k+4
        master=cvs(mid$(inpSTR$,k,4)):k=k+4
        master = INT(master)
        IF master < 0 OR master > 1 THEN master = 0
        beep
        COLOR 10, 0
        LOCATE 1, 24: PRINT "UPDATED";
        COLOR 7, 0
130     RETURN


        'SUBROUTINE: Clear error codes
140     FOR i = 1 TO 5
         SOURCEs(i, 1) = 0
         SOURCEs(i, 2) = 0
         SOURCEs(i, 0) = 0
        NEXT i
        FOR i = 1 TO 64
         SWITCHs%(i) = 0
        NEXT i
        FOR i = 1 TO 47
         DEVICEs(i) = 0
        NEXT i
        'DEVICEs(57) = 0
        FOR i = 1 TO 4
        SOURCEs(i, 3) = 0
        NEXT i
        HABfuelleak = 0
        AYSEfuelleak = 0
        WINDref = -1
        windACC = 0
        WINDangle = 0
        Zufo = 2
        Zref = 0
        Zrefalt = 0
        Zangle = 0
        Zorient = 0
        Zaccel = 0
        Ztarg = 38
        master = 0
        AUTOupdate = -1
        GOSUB 400
        RETURN


        'SUBROUTINE: Calculate orbit parameters
        'Calculate gravitaional attraction to reference object
300     difx = Px(ref, 3) - Px(28, 3)
        dify = Py(ref, 3) - Py(28, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        A = G * P(ref, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Vref = SQR(G * P(ref, 4) / R)
        Aref = angle
        Dref = R
        ACCref = A
        
        IF Zref = Ztrg THEN ZtrgAngle = 0: GOTO 311
        difx = Px(Zref, 3) - Px(Ztrg, 3)
        dify = Py(Zref, 3) - Py(Ztrg, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        A = G * P(ref, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        ZtrgAngle = angle


        'Calculate gravitational attraction to target object
311     difx = Px(targ, 3) - Px(28, 3)
        dify = Py(targ, 3) - Py(28, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF R < .1 THEN R = .1
        A = G * P(targ, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Vtarg = SQR(G * P(targ, 4) / R)
        Atarg = angle
        Dtarg = R
        Acctarg = A
        VVx = Vx(targ) - Vx(28)
        VVy = Vy(targ) - Vy(28)
        IF VVy = 0 THEN IF VVx < 0 THEN Vvangle = .5 * 3.1415926535# ELSE Vvangle = 1.5 * 3.1415926535# ELSE Vvangle = ATN(VVx / VVy)
        IF VVy > 0 THEN Vvangle = Vvangle + 3.1415926535#
        IF Vvangle < 0 THEN Vvangle = Vvangle + 6.283185
        VangleDIFF = Atarg - Vvangle
        AtoTARG = Acctarg
        IF COS(VangleDIFF) <> 0 AND Dtarg - P(targ, 5) <> 0 THEN AtoTARG = AtoTARG + ((((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2) / (2 * (Dtarg - P(targ, 5)))) * COS(VangleDIFF))



        ' Calculate atmospheric effects
        FOR i = 1 TO 34
         IF i = 28 THEN 321
         IF i = 32 THEN 321
         dist = SQR((Px(i, 3) - Px(28, 3)) ^ 2 + (Py(i, 3) - Py(28, 3)) ^ 2)
         IF dist <= P(i, 5) + (1000 * P(i, 10)) THEN atm = i: Ratm = (dist - P(i, 5)) / 1000
321     NEXT i
        IF atm = 0 THEN 322
        VVrx = Vx(atm) - Vx(28)
        VVry = Vy(atm) - Vy(28)
        IF VVry = 0 THEN IF VVrx < 0 THEN VvRangle = .5 * 3.1415926535# ELSE VvRangle = 1.5 * 3.1415926535# ELSE VvRangle = ATN(VVrx / VVry)
        IF VVry > 0 THEN VvRangle = VvRangle + 3.1415926535#
        IF VvRangle < 0 THEN VvRangle = VvRangle + 6.283185
        VVr = SQR((VVrx ^ 2) + (VVry ^ 2))
        IF Ratm < 0 THEN Pr = P(atm, 8) ELSE Pr = P(atm, 8) * (2.71828 ^ (-1 * Ratm / P(atm, 9)))
        Are = Pr * VVr * VVr * .0002
        IF Are * ts > VVr / 2 THEN Are = (VVr / 2) / ts
322     DelVvRangle = VvRangle - Sangle
        



       
        'Calculate gravitational attraction to UFO
        IF UFOdisp = 0 THEN 301
        IF UFOdisp = 1 THEN zr1 = 38: zr2 = Zref
        IF UFOdisp = 2 THEN zr1 = 38: zr2 = Ztrg
        IF UFOdisp = 3 THEN zr1 = Ztrg: zr2 = Zref
        difx = Px(zr1, 3) - Px(zr2, 3)
        dify = Py(zr1, 3) - Py(zr2, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF R = 0 THEN A = 0 ELSE A = G * P(zr2, 4) / (R ^ 2)
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        IF R = 0 THEN VrefUFO = 0 ELSE VrefUFO = SQR(G * P(zr2, 4) / R)
        Aufo = angle
        Dufo = R
        AccUFO = A
        VVx = Vx(zr2) - Vx(zr1)
        VVy = Vy(zr2) - Vy(zr1)
        IF VVy = 0 THEN IF VVx < 0 THEN Vvangle = .5 * 3.1415926535# ELSE Vvangle = 1.5 * 3.1415926535# ELSE Vvangle = ATN(VVx / VVy)
        IF VVy > 0 THEN Vvangle = Vvangle + 3.1415926535#
        IF Vvangle < 0 THEN Vvangle = Vvangle + 6.283185
        VangleDIFFufo = Aufo - Vvangle
        IF COS(VangleDIFFufo) <> 0 AND Dufo - P(zr2, 5) <> 0 THEN AccUFO = AccUFO + ((((Vx(zr2) - Vx(zr1)) ^ 2 + (Vy(zr2) - Vy(zr1)) ^ 2) / (2 * (Dufo - P(zr2, 5)))) * COS(VangleDIFFufo))
       

       
301     VVx = 0 - Vx(28)
        VVy = 0 - Vy(28)
        IF VVy = 0 THEN IF VVx < 0 THEN Vvangle = .5 * 3.1415926535# ELSE Vvangle = 1.5 * 3.1415926535# ELSE Vvangle = ATN(VVx / VVy)
        IF VVy > 0 THEN Vvangle = Vvangle + 3.1415926535#
        IF Vvangle < 0 THEN Vvangle = Vvangle + 6.283185


        'Calculate reference velocities
        Vhab = SQR(Vx(28) ^ 2 + Vy(28) ^ 2)
        Vrefhab = SQR((Vx(28) - Vx(ref)) ^ 2 + (Vy(28) - Vy(ref)) ^ 2)
        Vtarghab = SQR((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)
        VcenTARG = SQR(((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)) * -1 * COS(VangleDIFF)
        VtanTARG = SQR(((Vx(28) - Vx(targ)) ^ 2 + (Vy(28) - Vy(targ)) ^ 2)) * ABS(SIN(VangleDIFF))
       
        IF UFOdisp > 0 THEN Dtarg = Dufo: Vtarghab = VrefUFO: Atarg = Aufo: AtoTARG = AccUFO
        IF UFOdisp > 0 THEN VcenTARG = SQR(((Vx(zr1) - Vx(zr2)) ^ 2 + (Vy(zr1) - Vy(zr2)) ^ 2)) * -1 * COS(VangleDIFFufo)
        IF UFOdisp > 0 THEN VtanTARG = SQR(((Vx(zr1) - Vx(zr2)) ^ 2 + (Vy(zr1) - Vy(zr2)) ^ 2)) * ABS(SIN(VangleDIFFufo))
               
        IF Sangle < 0 THEN Sangle = 6.2831852# + Sangle
        RETURN



        'SUBROUTINE: Write telemetry data to screen
400     COLOR 11: LOCATE 1, 35: PRINT "               REFERENCE      ";
        IF UFOdisp = 0 THEN PRINT "    TARGET";
        IF UFOdisp = 1 THEN PRINT "UFO to REF";
        IF UFOdisp = 2 THEN PRINT "UFO to TRG";
        IF UFOdisp = 3 THEN PRINT "TRG to REF";
        COLOR 13
        LOCATE 2, 35: PRINT "                "; nme$(ref); "        ";
        IF UFOdisp = 0 THEN PRINT nme$(targ);  ELSE PRINT nme$(zr2);
        COLOR 11: LOCATE 3, 35: PRINT "DISTANCE: ";
        COLOR 15
        IF UFOdisp = 0 THEN Dtarg = Dtarg - P(targ, 5) - P(28, 5) ELSE Dtarg = Dtarg - P(zr2, 5) - P(zr1, 5)
        IF Dref > 99999999999# THEN PRINT USING "##.#######^^^^"; Dref / 1000;  ELSE PRINT USING "###,###,###.##"; (Dref - P(ref, 5) - P(28, 5)) / 1000;
        IF Dtarg > 99999999999# THEN PRINT USING "  ##.#######^^^^"; Dtarg / 1000;  ELSE PRINT USING "#####,###,###.##"; Dtarg / 1000;
        COLOR 11: LOCATE 4, 35: PRINT "VELOCITY: ";
        COLOR 15
        IF ABS(Vrefhab) > 99999999999# THEN PRINT USING "##.#######^^^^"; Vrefhab / 1000;  ELSE PRINT USING "###,###,###.##"; Vrefhab / 1000;
        IF ABS(Vtarghab) > 99999999999# THEN PRINT USING "  ##.#######^^^^"; Vtarghab / 1000;  ELSE PRINT USING "#####,###,###.##"; Vtarghab / 1000;
        COLOR 11: LOCATE 5, 35: PRINT "  CEN:                  ";
        COLOR 15
        IF ABS(VcenTARG) > 99999999999# THEN PRINT USING "  ##.#######^^^^"; VcenTARG / 1000;  ELSE PRINT USING "#####,###,###.##"; VcenTARG / 1000;
        COLOR 11: LOCATE 6, 35: PRINT "  TAN:                  ";
        COLOR 15
        IF ABS(VtanTARG) > 99999999999# THEN PRINT USING "  ##.#######^^^^"; VtanTARG / 1000;  ELSE PRINT USING "#####,###,###.##"; VtanTARG / 1000;
        COLOR 11: LOCATE 7, 35: PRINT "ANGLE:    ";
        COLOR 15
        PRINT USING "###,###,###.##"; Aref * RAD;
        PRINT USING "#####,###,###.##"; Atarg * RAD;
        COLOR 11: LOCATE 8, 35: PRINT "STOP ACC:               ";
        COLOR 15
        IF ABS(AtoTARG) > 999999999# THEN PRINT USING "  ##.#######^^^^"; AtoTARG;  ELSE PRINT USING "#####,###,###.##"; AtoTARG;
              
        IF AYSE = 150 THEN thrust = 64000000#: Hmass = fuel + AYSEfuel + 20275000 ELSE thrust = 175000: Hmass = fuel + 275000
        Haccel = (thrust * eng) / Hmass
        COLOR 11: LOCATE 9, 35: PRINT "ENGINE:   "; : COLOR 15: PRINT USING "####.###"; eng;
        COLOR 14 * SRB: LOCATE 9, 53: PRINT "SRB";
        COLOR 11: LOCATE 10, 35: PRINT "ACCEL:    "; : COLOR 15: PRINT USING "####.###"; Haccel;
        COLOR 11: LOCATE 11, 35: PRINT "DENSITY:  "; : COLOR 15: PRINT USING "####.###"; Pr;
        COLOR 11: LOCATE 12, 35: PRINT "H fuel:   "; : COLOR 15: PRINT USING "########"; fuel;
        COLOR 11: LOCATE 13, 35: PRINT "A fuel:   "; : COLOR 15: PRINT USING "########"; AYSEfuel;
        COLOR 11: LOCATE 9, 60: PRINT "HEADING:"; : COLOR 15: PRINT USING "####.##"; Sangle * RAD;
        COLOR 11: LOCATE 10, 61: PRINT "COURSE:"; : COLOR 15: PRINT USING "####.##"; Vvangle * RAD;
        COLOR 14 * para: LOCATE 13, 67: PRINT "CHUTE";
        COLOR 11: LOCATE 11, 68: PRINT "DRAG: "; : COLOR 15: IF Are < 9999.99 THEN PRINT USING "####.##"; Are;  ELSE PRINT USING "####.##"; 9999.99;
        COLOR 11: LOCATE 12, 67: PRINT "V"; CHR$(237); "ATM: "; : COLOR 15: PRINT USING "####.##"; DelVvRangle * RAD;
        COLOR 11: LOCATE 13, 68: PRINT "RCSP:"; : COLOR 15: PRINT USING "#####"; vernP!
        COLOR 11: LOCATE 14, 35: PRINT "NAV MODE: ";
        COLOR 15
          IF Sflag = 0 THEN PRINT "ccw prograde  "; : GOTO 401
          IF Sflag = 4 THEN PRINT "ccw retrograde"; : GOTO 401
          IF Sflag = 1 THEN PRINT "manual        "; : GOTO 401
          IF Sflag = 2 THEN PRINT "approach targ "; : GOTO 401
          IF Sflag = 5 THEN PRINT "pro Vtrg      "; : GOTO 401
          IF Sflag = 6 THEN PRINT "retr Vtrg     "; : GOTO 401
          IF Sflag = 3 THEN PRINT "depart ref    ";
401     COLOR 11: LOCATE 15, 35: PRINT "TIME:     "; : COLOR 15: PRINT USING "####"; year; : LOCATE 15, 51: PRINT USING "###"; day; hr; min; sec;
        COLOR 11: LOCATE 16, 35: PRINT "F rate:     "; : COLOR 15: PRINT USING "##.##"; ts;
       
        COLOR 14, 0
        LOCATE 16, 17: IF WINDref = -1 THEN PRINT "     OFF";  ELSE PRINT nme$(WINDref);
        LOCATE 17, 19: PRINT USING "####.#"; windACC;
        LOCATE 18, 20
        IF WINDangle = 0 THEN PRINT "   IN";
        IF WINDangle = 180 THEN PRINT "  OUT";
        IF WINDangle = 90 THEN PRINT "RIGHT";
        IF WINDangle = 270 THEN PRINT " LEFT";
       
        COLOR 11
        RETURN


        'SUBROUTINE: Timed telemetry retrieval
800     k=1
        locate 25, 11:print "         ";
801     OPEN "R", #1, "OSBACKUP.RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1427 then locate 25,11:print "ORB telem";:goto 802
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        IF left$(ORBITversion$,5) = "XXXXX" THEN RUN "orbit5vs"
        IF ORBITversion$ <> "ORBIT5S" THEN locate 25,11:print "ORB telem";
        if chkCHAR1$=chkCHAR2$ then  803
        k=k+1
        if k<3 then 801
        locate 25,11:print "ORB telem";
        goto 802           

803     k=2+15
        eng = cvs(mid$(inpSTR$,k,4)):k=k+4
        vflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Aflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        Sflag = cvi(mid$(inpSTR$,k,2)):k=k+18
        Sangle = cvd(mid$(inpSTR$,k,4)):k=k+6
        targ = cvi(mid$(inpSTR$,k,2)):k=k+2
        ref = cvi(mid$(inpSTR$,k,2)):k=k+4
        Cdh = cvs(mid$(inpSTR$,k,4)):k=k+4
        SRB = cvs(mid$(inpSTR$,k,4)):k=k+6
        dte = cvi(mid$(inpSTR$,k,2)):k=k+2
        ts = cvd(mid$(inpSTR$,k,8)):k=k+16
        vernP! = cvs(mid$(inpSTR$,k,4)):k=k+4
        Eflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        year = cvi(mid$(inpSTR$,k,2)):k=k+2
        day = cvi(mid$(inpSTR$,k,2)):k=k+2
        hr = cvi(mid$(inpSTR$,k,2)):k=k+2
        min = cvi(mid$(inpSTR$,k,2)):k=k+2
        sec = cvd(mid$(inpSTR$,k,8)):k=k+62
        LONGtarg = cvs(mid$(inpSTR$,k,4)):k=k+12
        FOR i = 1 TO 39
         Px(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Py(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Vx(i) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Vy(i) = cvd(mid$(inpSTR$,k,8)):k=k+8
        NEXT i
        fuel = cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEfuel = cvs(mid$(inpSTR$,k,4)):k=k+4

        IF Cdh > .004 then para=1 ELSE para = 0       
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3): Vx(37) = Vx(3): Vy(37) = Vy(3)
        IF vernP! > 999 THEN vernP! = 999
        IF vernP! < 0 THEN vernP! = 0
        Ltx = (P(ref, 5) * SIN(LONGtarg))
        Lty = (P(ref, 5) * COS(LONGtarg))
        Px(40, 3) = Px(ref, 3) + Ltx
        Py(40, 3) = Py(ref, 3) + Lty
        Vx(40) = Vx(ref)
        Vy(40) = Vy(ref)
802     RETURN


830     k=1
        locate 25, 1:print "         ";
833     OPEN "R", #1, "ORBITSSE.RND", 1159
        inpSTR$=space$(1159)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1159 then locate 25, 1:color 12:print "ENG telem";:goto 831
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 832
        k=k+1
        if k<3 then 833
        locate 25, 1:color 12:print "ENG telem";
        goto 831
        
832     k = 211
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
831     RETURN


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
        DATA "     Ida"
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
        DATA "  progrd"
        DATA "retrogrd"
        DATA " deptarg"
        DATA " apptarg"


2000    IF Zufo = 1 THEN Zufo = 2 ELSE Zufo = 1
        RETURN
2010    Zref = Zref + 1
        IF Zref = 36 THEN Zref = 0
        RETURN
2020
        IF Zrefalt < 10000000 THEN Zrefalt = Zrefalt + 10000
        IF Zrefalt >= 10000000 AND Zrefalt < 100000000 THEN Zrefalt = Zrefalt + 100000
        IF Zrefalt >= 100000000 AND Zrefalt < 1000000000 THEN Zrefalt = Zrefalt + 1000000
        IF Zrefalt >= 1000000000 THEN Zrefalt = Zrefalt + 10000000
        'IF Zrefalt > 10000000 THEN Zrefalt = 0
        RETURN
2030    Zorient = Zorient + 1
        IF Zorient = 4 THEN Zorient = 0
        RETURN
2040    Zaccel = Zaccel + 1
        IF Zaccel > 500 THEN Zaccel = 0
        RETURN
2050    Ztarg = Ztarg + 1
        IF Ztarg = 40 THEN Ztarg = 0
        RETURN
2060    Zangle = Zangle + .0087266
        IF Zangle > 6.2831853# THEN Zangle = 0
        RETURN
2070    Ztrg = Ztrg + 1
        IF Ztrg = 36 THEN Ztrg = 0
        RETURN

2110    Zref = Zref - 1
        IF Zref < 0 THEN Zref = 35
        RETURN
2120    Zrefalt = Zrefalt - 10000
        IF Zrefalt <= 10000000 THEN Zrefalt = Zrefalt - 10000
        IF Zrefalt > 10000000 AND Zrefalt <= 100000000 THEN Zrefalt = Zrefalt - 100000
        IF Zrefalt > 100000000 AND Zrefalt <= 1000000000 THEN Zrefalt = Zrefalt - 1000000
        IF Zrefalt > 1000000000 THEN Zrefalt = Zrefalt - 100000000
        IF Zrefalt < 0 THEN Zrefalt = 10000000
        RETURN
2130    Zorient = Zorient - 1
        IF Zorient < 0 THEN Zorient = 3
        RETURN
2140    Zaccel = Zaccel - 1
        IF Zaccel < 0 THEN Zaccel = 500
        RETURN
2150    Ztarg = Ztarg - 1
        IF Ztarg < 0 THEN Ztarg = 39
        RETURN
2160    Zangle = Zangle - .0087266
        IF Zangle < 0 THEN Zangle = 2 * 3.1415926535#
        RETURN
2170    Ztrg = Ztrg - 1
        IF Ztrg < 0 THEN Ztrg = 35
        RETURN

3000    COLOR 11, 0: LOCATE 20, 1: PRINT "BUS:"; : COLOR 14, 0: PRINT " VOLTS";
        LOCATE 21, 1: COLOR 11, 0: PRINT "  1:"; : COLOR 10, 0: PRINT USING "######"; Vbus1;
        LOCATE 22, 1: COLOR 11, 0: PRINT "  2:"; : COLOR 10, 0: PRINT USING "######"; Vbus2;
        LOCATE 23, 1: COLOR 11, 0: PRINT "  3:"; : COLOR 10, 0: PRINT USING "######"; Vbus3;
        LOCATE 24, 1: COLOR 11, 0: PRINT "  4:"; : COLOR 10, 0: PRINT USING "######"; Vbus4;
        COLOR 14, 0: LOCATE 20, 13: PRINT "CURRENT  SHORT";
        LOCATE 21, 13: COLOR 10, 0: PRINT USING "#######"; Ibus1;
        LOCATE 22, 13: COLOR 10, 0: PRINT USING "#######"; Ibus2;
        LOCATE 23, 13: COLOR 10, 0: PRINT USING "#######"; Ibus3;
        LOCATE 24, 13: COLOR 10, 0: PRINT USING "#######"; Ibus4;
        LOCATE 20, 30: COLOR 11, 0: PRINT "SOURCE:"; : COLOR 14, 0: LOCATE 20, 38: PRINT "OUTPUT";
        LOCATE 21, 31: COLOR 11, 0: PRINT "H Rct:"; : COLOR 10, 0: PRINT USING "#######"; Is1;
        LOCATE 22, 31: COLOR 11, 0: PRINT "   FC:"; : COLOR 10, 0: PRINT USING "#######"; Is2;
        LOCATE 23, 31: COLOR 11, 0: PRINT " BAT1:"; : COLOR 10, 0: PRINT USING "#######"; Is3;
        LOCATE 25, 31: COLOR 11, 0: PRINT "A Rct:"; : COLOR 10, 0: PRINT USING "#######"; Is5;
        LOCATE 24, 31: COLOR 11, 0: PRINT " BAT3:"; : COLOR 10, 0: PRINT USING "#######"; Is4;
        COLOR 14, 0: LOCATE 20, 45: PRINT "TEMP  VOLTS  MALFC  FIX";
        LOCATE 21, 45:  COLOR 10, 0: PRINT USING "####"; Htemp;
        LOCATE 22, 45:  COLOR 10, 0: PRINT USING "####"; FCtemp;
        LOCATE 23, 45:  COLOR 10, 0: PRINT USING "####"; BATT1temp;
        LOCATE 25, 45:  COLOR 10, 0: PRINT USING "####"; Atemp;
        LOCATE 24, 45:  COLOR 10, 0: PRINT USING "####"; BATT3temp;
        bckgADJ = SGN(UFOflag + DEVICEselect)
        FOR i = 1 TO 5
         IF SOURCEs(0, 1) = i AND SOURCEs(0, 2) = 1 THEN Bclr = 1 ELSE Bclr = 0
         IF SOURCEs(i, 1) <> 0 THEN COLOR 12, Bclr ELSE COLOR 10, Bclr * ABS(1 - bckgADJ)
         LOCATE 20 + i, 50: PRINT USING "######"; SOURCEs(i, 1) + SOURCEs(i, 4);
        
         IF SOURCEs(0, 1) = i AND SOURCEs(0, 2) = 2 THEN Bclr = 1 ELSE Bclr = 0
         IF SOURCEs(i, 2) <> 0 THEN COLOR 12, Bclr ELSE COLOR 10, Bclr * ABS(1 - bckgADJ)
         LOCATE 20 + i, 58: PRINT USING "#####"; SOURCEs(i, 2);
        
         IF SOURCEs(0, 1) = i AND SOURCEs(0, 2) = 3 THEN Bclr = 1 ELSE Bclr = 0
         IF SOURCEs(i, 0) <> 0 THEN COLOR 10, Bclr ELSE COLOR 2, Bclr * ABS(1 - bckgADJ)
         LOCATE 20 + i, 65: PRINT USING "###"; SOURCEs(i, 0);
        
         IF SOURCEs(0, 1) = i AND SOURCEs(0, 2) = 4 THEN Bclr = 1 ELSE Bclr = 0
         IF SOURCEs(i, 3) <> 0 THEN COLOR 12, Bclr ELSE COLOR 10, Bclr * ABS(1 - bckgADJ)
         IF i < 5 THEN LOCATE 20 + i, 22: PRINT USING "#####"; SOURCEs(i, 3);
        NEXT i
        RETURN

4000    FOR ij = 17 TO 25
         LOCATE ij, 70: PRINT "           ";
        NEXT ij
        LOCATE 17, 53: PRINT "               ";
        IF UFOflag = 0 THEN Ztarg = 38: Zufo = 2: MSLflag = 0
        RETURN


4200    'check codes
        z3 = switchlist(i, 3)
        IF LEFT$(switchlist$(i, 1), 3) = "frg" THEN 4220
        IF LEFT$(switchlist$(i, 1), 3) = "INS" THEN 4230
        IF LEFT$(switchlist$(i, 1), 3) = "NAV" THEN 4230
        IF LEFT$(switchlist$(i, 1), 3) = "TRN" THEN 4230
        IF LEFT$(switchlist$(i, 1), 4) = "RADS" THEN 4230
       
        IF SWITCHs%(z3) > 0 THEN clrfg = 12
        IF z3 <= 33 AND DEVICEs(9 + z3) > 0 THEN clrfg = 12
        RETURN

4220    IF DEVICEs(z3 - 59) > 0 THEN clrfg = 12
        IF DEVICEs(z3 - 56) > 0 THEN clrfg = 12
        IF DEVICEs(z3 - 53) > 0 THEN clrfg = 12
        RETURN

4230    IF SWITCHs%(z3) > 0 THEN clrfg = 12
        RETURN




4300    COLOR 13, 0
        labelOFFSET = 0
        IF LEFT$(switchlist$(y, 1), 3) = "frg" THEN labelOFFSET = 7
        IF LEFT$(switchlist$(y, 1), 3) = "INS" THEN labelOFFSET = 14
        IF LEFT$(switchlist$(y, 1), 3) = "NAV" THEN labelOFFSET = 21
        IF LEFT$(switchlist$(y, 1), 3) = "TRN" THEN labelOFFSET = 27
        IF LEFT$(switchlist$(y, 1), 4) = "RADS" THEN labelOFFSET = 29
        LOCATE 18, 70
        PRINT switchlist$(y, 1);
        FOR i = 1 TO 7
         IF malf(mlf, 0) > malf(mlf + labelOFFSET, 2) THEN malf(mlf, 0) = malf(mlf + labelOFFSET, 2)
         IF malf(mlf, 0) < malf(mlf + labelOFFSET, 1) THEN malf(mlf, 0) = malf(mlf + labelOFFSET, 1)
         IF mlf = i THEN clrb = 1 ELSE clrb = 0
         IF ((2 ^ (i - 1)) AND switchlist(DEVICEselect, 5)) = 0 THEN 4310
         COLOR 11, clrb: LOCATE 18 + i, 70: PRINT malfNAME$(i + labelOFFSET); : COLOR 10, clrb: PRINT USING "####"; malf(i, 0);
4310    NEXT i
        'z$ = INPUT$(1)
        RETURN

4400    'retrieve codes
        IF LEFT$(switchlist$(y, 1), 3) = "frg" THEN 4420
        IF LEFT$(switchlist$(y, 1), 3) = "INS" THEN 4430
        IF LEFT$(switchlist$(y, 1), 3) = "NAV" THEN 4440
        IF LEFT$(switchlist$(y, 1), 3) = "TRN" THEN 4450
        IF LEFT$(switchlist$(y, 1), 4) = "RADS" THEN 4460

        malf(1, 0) = (3 AND SWITCHs%(z2))
        malf(2, 0) = (60 AND SWITCHs%(z2))
        IF malf(2, 0) > 12 THEN malf(2, 0) = malf(2, 0) / -4
        malf(2, 0) = malf(2, 0) / 4
        malf(3, 0) = (960 AND SWITCHs%(z2)) / 64
        malf(4, 0) = (3072 AND SWITCHs%(z2)) / 1024
        malf(5, 0) = (15 AND DEVICEs(9 + z2))
        malf(6, 0) = (240 AND DEVICEs(9 + z2)) / 16
        malf(7, 0) = (4096 AND SWITCHs%(z2)) / 4096
        RETURN

4420    malf(1, 0) = (3 AND DEVICEs(z2 - 59))
        malf(2, 0) = (12 AND DEVICEs(z2 - 59)) / 4
        malf(3, 0) = (240 AND DEVICEs(z2 - 59)) / 16
        malf(4, 0) = (3 AND DEVICEs(z2 - 56))
        malf(5, 0) = (12 AND DEVICEs(z2 - 56)) / 4
        malf(6, 0) = (240 AND DEVICEs(z2 - 56)) / 16
        malf(7, 0) = DEVICEs(z2 - 53)
        IF malf(2, 0) = 0 THEN 4421
        IF malf(2, 0) = 1 THEN malf(2, 0) = 2 ELSE malf(2, 0) = 1
4421    IF malf(5, 0) = 0 THEN 4422
        IF malf(5, 0) = 1 THEN malf(5, 0) = 2 ELSE malf(5, 0) = 1
4422    RETURN

4430    malf(1, 0) = (1 AND SWITCHs%(z2))
        malf(2, 0) = (2 AND SWITCHs%(z2)) / 2
        malf(3, 0) = (60 AND SWITCHs%(z2))
        IF malf(3, 0) > 12 THEN malf(3, 0) = malf(3, 0) / -4
        malf(3, 0) = malf(3, 0) / 4
        malf(4, 0) = (64 AND SWITCHs%(z2)) / 64
        malf(5, 0) = (128 AND SWITCHs%(z2)) / 128
        malf(6, 0) = (256 AND SWITCHs%(z2)) / 256
        malf(7, 0) = (512 AND SWITCHs%(z2)) / 512
        RETURN

4440    malf(1, 0) = (1 AND SWITCHs%(z2))
        malf(2, 0) = (2 AND SWITCHs%(z2)) / 2
        malf(3, 0) = (4 AND SWITCHs%(z2)) / 4
        malf(4, 0) = (8 AND SWITCHs%(z2)) / 8
        malf(5, 0) = (16 AND SWITCHs%(z2)) / 16
        malf(6, 0) = (32 AND SWITCHs%(z2)) / 32
        RETURN

4450    malf(1, 0) = (3 AND SWITCHs%(z2))
        malf(2, 0) = (12 AND SWITCHs%(z2)) / 4
        RETURN

4460    malf(1, 0) = (1 AND SWITCHs%(z2))
        malf(2, 0) = (6 AND SWITCHs%(z2)) / 2
        malf(3, 0) = (8 AND SWITCHs%(z2)) / 8
        malf(4, 0) = (48 AND SWITCHs%(z2)) / 16
        malf(5, 0) = (64 AND SWITCHs%(z2)) / 64
        malf(6, 0) = (384 AND SWITCHs%(z2)) / 128
        RETURN

4500    'save codes
        FOR i = 18 TO 25
         LOCATE i, 70: PRINT SPACE$(11);
        NEXT i
        IF LEFT$(switchlist$(y, 1), 3) = "frg" THEN 4520
        IF LEFT$(switchlist$(y, 1), 3) = "INS" THEN 4530
        IF LEFT$(switchlist$(y, 1), 3) = "NAV" THEN 4540
        IF LEFT$(switchlist$(y, 1), 3) = "TRN" THEN 4550
        IF LEFT$(switchlist$(y, 1), 4) = "RADS" THEN 4560

        SWITCHs%(z2) = malf(1, 0)
        IF malf(2, 0) < 0 THEN malf(2, 0) = malf(2, 0) * -4
        SWITCHs%(z2) = SWITCHs%(z2) + (4 * malf(2, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (64 * malf(3, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (1024 * malf(4, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (4096 * malf(7, 0))
        DEVICEs(9 + z2) = malf(5, 0) + (16 * malf(6, 0))
        RETURN
       
4520    IF malf(2, 0) = 0 THEN 4521
        IF malf(2, 0) = 1 THEN malf(2, 0) = 2 ELSE malf(2, 0) = 1
4521    IF malf(5, 0) = 0 THEN 4522
        IF malf(5, 0) = 1 THEN malf(5, 0) = 2 ELSE malf(5, 0) = 1
4522    DEVICEs(z2 - 59) = malf(1, 0) + (4 * malf(2, 0)) + (16 * malf(3, 0))
        DEVICEs(z2 - 56) = malf(4, 0) + (4 * malf(5, 0)) + (16 * malf(6, 0))
        DEVICEs(z2 - 53) = malf(7, 0)
        RETURN

4530    SWITCHs%(z2) = malf(1, 0)
        SWITCHs%(z2) = SWITCHs%(z2) + (2 * malf(2, 0))
        IF malf(3, 0) < 0 THEN malf(3, 0) = malf(3, 0) * -4
        SWITCHs%(z2) = SWITCHs%(z2) + (4 * malf(3, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (64 * malf(4, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (128 * malf(5, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (256 * malf(6, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (512 * malf(7, 0))
        RETURN

4540    SWITCHs%(z2) = malf(1, 0)
        SWITCHs%(z2) = SWITCHs%(z2) + (2 * malf(2, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (4 * malf(3, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (8 * malf(4, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (16 * malf(5, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (32 * malf(6, 0))
        RETURN

4550    SWITCHs%(z2) = malf(1, 0)
        SWITCHs%(z2) = SWITCHs%(z2) + (4 * malf(2, 0))
        RETURN

4560    SWITCHs%(z2) = malf(1, 0)
        SWITCHs%(z2) = SWITCHs%(z2) + (2 * malf(2, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (8 * malf(3, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (16 * malf(4, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (64 * malf(5, 0))
        SWITCHs%(z2) = SWITCHs%(z2) + (128 * malf(6, 0))
        RETURN



4390    DATA "Malf:  ", 0, 3
        DATA "Res:   ",-3, 3
        DATA "Temp:  ", 0,15
        DATA "Short: ", 0, 3
        DATA "Leaks: ", 0,15
        DATA "Leaks: ", 0,15
        DATA "Swtch: ", 0, 1
        DATA "Pmp1:  ", 0, 3
        DATA "temp:  ", 0, 2
        DATA "leak:  ", 0, 15
        DATA "Pmp2:  ", 0, 3
        DATA "temp:  ", 0, 2
        DATA "leak:  ", 0, 15
        DATA "LeakS: ", 0, 15
        DATA "refVo: ", 0, 1
        DATA "INS:   ", 0, 1
        DATA "ucRot: ",-3, 3
        DATA "CCWoff:", 0, 1
        DATA "CWoff: ", 0, 1
        DATA "Vc&Vt: ", 0, 1
        DATA "ApoPer:", 0, 1
        DATA "NAVtrg:", 0, 1
        DATA "GNC:   ", 0, 1
        DATA "NAVref:", 0, 1
        DATA "ApoPer:", 0, 1
        DATA "Pch:   ", 0, 1
        DATA "ACC:   ", 0, 1
        DATA "TRN1:  ", 0, 3
        DATA "TRN2:  ", 0, 3
        DATA "RAD1ex:", 0, 1
        DATA "funct: ", 0, 3
        DATA "RAD2ex:", 0, 1
        DATA "funct: ", 0, 3
        DATA "RAD3ex:", 0, 1
        DATA "funct: ", 0, 3



5000    'IF ERL = 800 OR ERL = 801 THEN tt = tt + .5: RESUME 803
        'IF ERL = 830 THEN tt = tt + .5: : CLOSE #1: RESUME 830
        'IF ERL = 900 THEN tt = tt + .5: RESUME 901
        'IF ERL = 100 THEN CLOSE #1: RESUME 110
        'IF ERL = 98 AND ERR = 76 THEN CLS : LOCATE 15, 5: PRINT "'"; zpath$; "' Path not found"; : RESUME 97
        'IF ERL = 98 AND ERR = 53 THEN CLS : LOCATE 15, 5: PRINT "Backup file not found in '"; zpath$; "'"; : RESUME 97
        LOCATE 1, 30: PRINT "unknown error: "; ERR; ERL
        z$ = INPUT$(1)
        END



6000    DATA  2,  1,  1, "a", "RAD1 ", 127
        DATA  3,  1,  2, "b", "RAD2 ", 127
        DATA  4,  1,  3, "c", "AGRAV", 127
        DATA  5,  1,  4, "1", "Rcon1",  15
        DATA  6,  1,  5, "2", "Rcon2",  15
        DATA  7,  1,  6, "d", "ACC1 ", 127
        DATA  8,  1,  7, "e", "ION1 ", 127
        DATA  9,  1,  8, "f", "ACC2 ", 127
        DATA 10,  1,  9, "g", "ION2 ", 127
        DATA 11,  1, 10, "h", "ACC3 ", 127
        DATA 12,  1, 11, "i", "ION3 ", 127
        DATA 13,  1, 12, "j", "ACC4 ", 127
        DATA 14,  1, 13, "k", "ION4 ", 127
        DATA  2,  9, 19, "l", "RCSP ",  15
        DATA  3,  9, 20, "m", "COM  ",  15
        DATA  4,  9, 21, "n", "LINE1",   1
        DATA  5,  9, 22, "o", "LINE2",   1
        DATA  6,  9, 23, "p", "LINE3",   1
        DATA  7,  9, 57, "q", "LINE4",   1
        DATA  8,  9, 34, "r", "Einj1",   1
        DATA  9,  9, 35, "s", "Einj2",   1
        DATA 10,  9, 36, "t", "DUMP ",   1
        DATA 11,  9, 37, "u", "LOAD ",   1
        DATA 12,  9, 38, "v", "Rinj1",   1
        DATA 13,  9, 39, "w", "Rinj2",   1
        DATA 14,  9, 40, "x", "FCinj",   1
        DATA  2, 17, 59, "P", "chute",   1
        DATA  3, 17, 54, "y", "NAV  ",  63
        DATA  4, 17, 51, "z", "INS  ",  63
        DATA  5, 17, 50, "0", "RADAR",  15
        DATA  6, 17, 58, "3", "LOS  ",   1
        DATA  7, 17, 55, "4", "dock ",   1
        DATA  8, 17, 52, "5", "pack ",  65
        DATA  9, 17, 47, "6", "heat ",   1
        DATA 10, 17, 48, "7", "mod  ",   1
        DATA 11, 17, 15, "8", "TRN  ",   3
        DATA 12, 17, 64, "9", "RADS ",  63
        DATA 13, 17, 60, "L", "frg1", 127
        DATA 14, 17, 61, "M", "frg2", 127
        DATA  2, 25, 27, "A", "Acon1",  95
        DATA  3, 25, 28, "B", "Acon2",  95
        DATA  4, 25, 29, "C", "GPD1 ",  95
        DATA  5, 25, 30, "D", "GPD2 ",  95
        DATA  6, 25, 31, "E", "GPD3 ",  95
        DATA  7, 25, 32, "F", "GPD4 ",  95
        DATA  8, 25, 33, "G", "TTC  ",  95
        DATA  9, 25, 41, "H", "DUMP ",   1
        DATA 10, 25, 42, "I", "LOAD ",   1
        DATA 11, 25, 43, "J", "Rinj1",   1
        DATA 12, 25, 44, "K", "Rinj2",   1
        DATA 13, 25, 62, "N", "frg3", 127
        DATA 14, 25, 63, "O", "SRB  ",   1
