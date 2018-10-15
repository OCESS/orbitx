        ON ERROR GOTO 3000
        DEFDBL A-Z
        DIM az(256)
        dim i as long
        dim j as long
        dim l as long
        open "R", #5, "marsTOPOLG.RND",2

        CLS
        OPEN "R", #2, "OSBACKUP.RND", 8
        inpSTR$=space$(8)
        GET #2, 1, inpSTR$
        inpFLAG$=right$(inpSTR$,7)
        outSTR$ = left$(inpSTR$,1)+"ORBIT5S"
        PUT #2, 1, outSTR$
        CLOSE #2
        MASRrefLAT=174.85

        filename$="MST"
        Zpath$=""
        IF inpFLAG$ = "XXXXXYY" THEN filename$="MSTRS": goto 51
        IF inpFLAG$ = "XXXXXXX" THEN GOTO 51
        LOCATE 5, 5
        PRINT "Telemetry Display Utility for ORBIT v. 5R"
        INPUT ; "    path to main program: ", Zpath$
        IF UCASE$(Zpath$) = "QUIT" THEN END
       
51      SCREEN 18
        for i=1 to 217
            if i<35 and kb<62 then kb=kb+2
            if i>31 and i<124 and kg<62 then kg=kg+2
            if i>62 and i<155 and kb>0 then kb=kb-2
            if i>93 and kr<62 then kr=kr+2
            if i>124 and i<186 and kg>0 then kg=kg-2
            if i>155 and kb<62 then kb=kb+2
            if i>186 and kg<62 then kg=kg+2
            palette i+16, (kr)+(256*kg)+(65536*kb)
        next i

        'PALETTE 1, 1 + (1 * 256) + (19 * 65536)
        'PALETTE 2, 10 + (10 * 256) + (10 * 65536)
        'PALETTE 3, 18 + (18 * 256) + (18 * 65536)
        'PALETTE 5, 25 + (25 * 256) + (25 * 65536)
        'PALETTE 7, 31 + (31 * 256) + (31 * 65536)
        'PALETTE 8, 36 + (36 * 256) + (36 * 65536)
        'PALETTE 10, 41 + (41 * 256) + (41 * 65536)
        'PALETTE 11, 46 + (46 * 256) + (46 * 65536)
        'PALETTE 13, 51 + (51 * 256) + (51 * 65536)
        ''PALETTE 5, 19 + (19 * 256) + (19 * 65536)
        ''PALETTE 1, 1 + (1 * 256) + (19 * 65536)
        ''PALETTE 11, 49 + (49 * 256) + (49 * 65536)
        DIM a(11, 20), P(40, 5), Ztel(50), Px(40, 3), Py(40, 3), ccc(456), nme$(40)

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
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
         INPUT #1, z
        NEXT i
        INPUT #1, z, z, z, z, z
        FOR i = 0 TO 35
         INPUT #1, z, z, z, z, z, z
        NEXT i
        FOR i = 0 TO 39
         INPUT #1, nme$(i)
        NEXT i
        nme$(40) = "TARGET"
        CLOSE #1

        a(2, 0) = 0
        a(2, 1) = 1
        a(2, 2) = 2
        a(2, 3) = 9
        a(2, 4) = 2
        a(2, 5) = 4
        a(2, 6) = 3
        a(2, 7) = 15
        a(2, 8) = 6
        a(2, 9) = 4
        a(2, 10) = 14
        a(2, 11) = 13
        a(2, 12) = 5
        a(2, 13) = 10
         a(2, 14) = 15
        a(2, 15) = 8
        a(1, 0) = 0
        a(1, 1) = 1
        a(1, 2) = 2
        a(1, 3) = 9
        a(1, 4) = 2
        a(1, 5) = 3    '4
        a(1, 6) = 15   '3
        a(1, 7) = 15
        a(1, 8) = 14
        a(1, 9) = 10
        a(1, 10) = 13
        a(1, 11) = 3  '4
        a(1, 12) = 5  '5
        a(1, 13) = 6
        a(1, 14) = 7
        a(1, 15) = 8
        a(3, 0) = 0
        a(3, 1) = 5
        a(3, 2) = 0
        a(3, 3) = 3
        a(3, 4) = 8
        a(3, 5) = 9
        a(3, 6) = 0
        a(3, 7) = 0
        a(3, 8) = 11
        a(3, 9) = 2
        a(3, 10) = 1
        a(3, 11) = 10
        a(3, 12) = 4
        a(3, 13) = 6
        a(3, 14) = 0
        a(3, 15) = 15
        a(4, 0) = 0
        a(4, 1) = 1
        a(4, 2) = 8
        a(4, 3) = 9
        a(4, 4) = 3
        a(4, 5) = 5
        a(4, 6) = 4
        a(4, 7) = 6
        a(4, 8) = 12
        a(4, 9) = 13
        a(4, 10) = 11
        a(4, 11) = 2
        a(4, 12) = 10
        a(4, 13) = 14
        a(4, 14) = 7
        a(4, 15) = 15
        a(5, 0) = 8
        a(5, 1) = 1
        a(5, 2) = 8
        a(5, 3) = 3
        a(5, 4) = 9
        a(5, 5) = 3
        a(5, 6) = 8
        a(5, 7) = 7
        a(5, 8) = 8
        a(5, 9) = 9
        a(5, 10) = 3
        a(5, 11) = 11
        a(5, 12) = 1
        a(5, 13) = 9
        a(5, 14) = 3
        a(5, 15) = 3
        a(6, 0) = 8
        a(6, 1) = 6
        a(6, 2) = 15
        a(6, 3) = 7
        a(6, 4) = 6
        a(6, 5) = 14
        a(6, 6) = 6
        a(6, 7) = 7
        a(6, 8) = 7
        a(6, 9) = 14
        a(6, 10) = 7
        a(6, 11) = 7
        a(6, 12) = 14
        a(6, 13) = 12
        a(6, 14) = 14
        a(6, 15) = 15
        a(7, 0) = 7
        a(7, 1) = 3
        a(7, 2) = 2
        a(7, 3) = 3
        a(7, 4) = 10
        a(7, 5) = 3
        a(7, 6) = 10
        a(7, 7) = 7
        a(7, 8) = 11
        a(7, 9) = 11
        a(7, 10) = 10
        a(7, 11) = 11
        a(7, 12) = 11
        a(7, 13) = 3
        a(7, 14) = 11
        a(7, 15) = 15
        a(8, 0) = 0
        a(8, 1) = 8
        a(8, 2) = 1
        a(8, 3) = 5
        a(8, 4) = 9
        a(8, 5) = 3
        a(8, 6) = 7
        a(8, 7) = 13
        a(8, 8) = 11
        a(8, 9) = 14
        a(8, 10) = 15
        a(11, 0) = 0
        a(11, 1) = 1
        a(11, 2) = 2
        a(11, 3) = 3
        a(11, 4) = 4
        a(11, 5) = 5
        a(11, 6) = 6
        a(11, 7) = 7
        a(11, 8) = 8
        a(11, 9) = 9
        a(11, 10) = 10
        a(11, 11) = 11
        a(11, 12) = 12
        a(11, 13) = 13
        a(11, 14) = 14
        a(11, 15) = 15
       




        P(0, 5) = 6.96E+08
        P(1, 5) = 4878000 / 2
        P(2, 5) = 12104000 / 2
        P(3, 5) = 12576000 / 2
        P(4, 5) = 6787000 / 2
        P(5, 5) = 143800000 / 2
        P(6, 5) = 120660000 / 2
        P(7, 5) = 52290000 / 2
        P(8, 5) = 49500000 / 2
        P(9, 5) = 3000000 / 2
        P(10, 5) = 3476000 / 2
        P(11, 5) = 11000
        P(12, 5) = 135000
        P(13, 5) = 1820000
        P(14, 5) = 1500000
        P(15, 5) = 2640000
        P(16, 5) = 2500000
        P(17, 5) = 530000
        P(18, 5) = 560000
        P(19, 5) = 765000
        P(20, 5) = 2560000
        P(21, 5) = 730000
        P(22, 5) = 665000
        P(23, 5) = 555000
        P(24, 5) = 800000
        P(25, 5) = 815000
        P(26, 5) = 1700000
        P(27, 5) = 1300000
        P(28, 5) = 80
        P(29, 5) = 40000 / 2
        P(30, 5) = 1400 / 2
        P(31, 5) = 960000 / 2
        P(32, 5) = 500
        P(33, 5) = 1800000
        P(34, 5) = 1287000
        P(35, 5) = 500
        P(36, 5) = 70
        P(38, 5) = 500
        P(39, 5) = 10
        
        
81      OPEN "R", #1, filename$+".RND", 26
        inpSTR$=space$(26)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 26 then 82
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$=chkCHAR2$ then 86
82      MST#=2015
        EST#=2015
        LONGtarg=0
        goto 90
86      k=2
        MST# = CVD(mid$(inpSTR$,k,8)):k=k+8
        EST# = CVD(mid$(inpSTR$,k,8)):k=k+8
        LONGtarg = CVD(mid$(inpSTR$,k,8))
        Dref = 3: clr = 11
        'print filename$
        'print LONGtarg
        'print inpSTR$
        'print len(inpSTR$)
        'z$=input$(1)
        'end
        'MST#=2015
        'EST#=2015
        'LONGtarg=0


90      if Dref<>4 then MAGmars=0
        IF Dref = 28 THEN Dref = 3
        IF Dref = 32 THEN Dref = 3
        'clr = clr + 1: IF clr = 5 THEN clr = 1
        filename$ = ""
        IF Dref = 3 THEN clr = 1: filename$ = "mggd.bmp"
        'IF Dref = 4 THEN clr = 2: filename$ = "mgstopo3.bmp"
        IF Dref = 4 THEN clr = 2: filename$ = "marsSMa.bmp"
        IF Dref = 2 THEN clr = 3: filename$ = "venusS.bmp"
        IF Dref = 10 THEN clr = 4: filename$ = "moon.bmp"
        IF Dref = 5 THEN clr = 4: filename$ = "jupiter.bmp"
        IF Dref = 20 THEN clr = 4: filename$ = "titan.bmp"
        IF Dref = 13 THEN clr = 4: filename$ = "io.bmp"
        IF Dref = 14 THEN clr = 4: filename$ = "europa.bmp"
        IF Dref = 15 THEN clr = 4: filename$ = "ganymede.bmp"
        IF Dref = 16 THEN clr = 4: filename$ = "callisto.bmp"
        IF Dref = 6 THEN clr = 6: filename$ = "saturn.bmp"
        IF Dref = 8 THEN clr = 5: filename$ = "neptune.bmp"
        IF Dref = 1 THEN clr = 4: filename$ = "mercury.bmp"
        IF Dref = 9 THEN clr = 4: filename$ = "pluto.bmp"
        IF Dref = 7 THEN clr = 7: filename$ = "uranus.bmp"
        IF Dref = 11 THEN clr = 4: filename$ = "phobos.bmp"
        IF Dref = 12 THEN clr = 11: filename$ = "hyper6g.bmp"
        IF Dref = 17 THEN clr = 4: filename$ = "enceldus.bmp"
        IF Dref = 18 THEN clr = 4: filename$ = "dione.bmp"
        IF Dref = 19 THEN clr = 4: filename$ = "callisto.bmp"      '"rhea.bmp"
        IF Dref = 21 THEN clr = 4: filename$ = "iapetus.bmp"
        IF Dref = 27 THEN clr = 4: filename$ = ""      '"charon.bmp"
        IF Dref = 26 THEN clr = 4: filename$ = "triton.bmp"      '"triton.bmp"
        IF Dref = 30 THEN clr = 4: filename$ = ""      '"borrelly.bmp"
        IF Dref = 33 THEN clr = 4: filename$ = ""      '"m2012a.bmp"
        IF Dref = 24 THEN clr = 4: filename$ = "titania.bmp"

        'filename$ = "m2012a.bmp"
        'filename4$ = "thermal.bmp"
        'filename2$ = "magnetic.bmp"
        'filename3$ = "moist.bmp"
        IF LEN(filename4$) > 0 THEN OPEN "R", #4, filename4$, 1: d$=" "
       
        'Draw planet surface
91      IF filename$ = "" THEN LINE (0, 0)-(639, 319), 0, BF: GOTO 99
        if MAGmars=1 then gosub 4000: goto 200
        if MAGmars=2 then gosub 4100: goto 200
        if MAGmars=3 then gosub 4200: goto 200
        OPEN "R", #1, filename$, 1
        a$=" "
        
        k = 1079
        FOR x = 0 TO 319
         FOR y = 0 TO 639
          GET #1, k, a$
          i = ASC(a$)
          ic = i
          'locate 29,1+(3*i):color i:print using "##";i;:color 7
          if Dref=4 then PSET (y, 319 - x), i: goto 93 
          if Dref=26 then goto 999 'if i=checkI then PSET (y, 319 - x), 15: goto 93 else PSET (y, 319 - x), 0: goto 93
          IF ic = 14 THEN ic = 15
          IF ic = 13 THEN ic = 14
          IF ic = 10 THEN ic = 11
          IF ic = 8 THEN ic = 10
          IF ic = 7 THEN ic = 8
          IF ic = 6 THEN ic = 7
          GOTO 92
          'IF i = 2 THEN i = 12
          az(i) = az(i) + 1: GOTO 93
999       if i <3 THEN PSET (y, 319 - x), 0: goto 93
          if i =3 THEN PSET (y, 319 - x), 1: goto 93
          if i =4 THEN PSET (y, 319 - x), 8: goto 93
          if i =5 THEN PSET (y, 319 - x), 4: goto 93
          if i =6 THEN PSET (y, 319 - x), 5: goto 93
          if i =7 THEN PSET (y, 319 - x), 6: goto 93
          if i =8 THEN PSET (y, 319 - x), 2: goto 93
          if i =9 THEN PSET (y, 319 - x), 9: goto 93
          if i =10 THEN PSET (y, 319 - x), 7: goto 93
          if i =11 THEN PSET (y, 319 - x), 10: goto 93
          if i =12 THEN PSET (y, 319 - x), 11: goto 93
          if i =13 THEN PSET (y, 319 - x), 14: goto 93
          if i >13 THEN PSET (y, 319 - x), 15: goto 93
          goto 93
          
          ij = 0
          IF LEN(filename4$) > 0 THEN GET #4, k, d$: ij = ASC(d$)
          IF Dref = 33 THEN ic = i ELSE ic = a(clr, i)
          'LOCATE 3, 1: PRINT filename4$;
          IF filename4$ <> "thermal.bmp" THEN 111
          IF ij < 15 THEN ic = ij
          IF ij = 11 THEN ic = 14
          IF ij = 3 THEN ic = 13
          GOTO 92

111       IF filename4$ <> "magnetic.bmp" THEN 112
          IF ij = 0 THEN ic = 0
          IF ij = 1 THEN ic = 1
          IF ij = 2 THEN ic = 2
          GOTO 92

         
112       IF filename4$ <> "moist.bmp" THEN 92
          IF ij < 15 THEN ic = ij
          'IF ij = 11 THEN ic = 14
          'IF ij = 3 THEN ic = 13
          GOTO 92
         
          'CLS
          'IF ij = 1 THEN ic = 5
          'IF ij = 2 THEN ic = 14
          'IF ij = 3 THEN ic = 13
          'IF ij = 4 THEN ic = 15
92        PSET (y, 319 - x), a(clr, i)'ic
93        k = k + 1
         NEXT y
        NEXT x
        checkI=checkI+1
    
'FOR i = 0 TO 256
' IF az(i) > 0 THEN PRINT i, az(i)
'NEXT i
'END
'        FOR gg = 1 TO 15
'         COLOR gg: LOCATE gg, 1: PRINT gg;
'        NEXT gg

        CLOSE #1
        if len(filename4$)>0 then CLOSE #4
        'FOR i = 0 TO 456
        ' IF ccc(i) > 0 THEN PRINT i, ccc(i)
        'NEXT i
        'z$ = INPUT$(1)
        'END

        'Drawn orbital path
99      x = 0
        'y = 80 * sin((x - 10) / 101.859164#)
        if Dref= 4 then y = 50 * SIN((x - MASRrefLAT) / 101.859164#) else y = 80 * sin((x - 10) / 101.859164#)
        PSET (x, 160 - y), 15
        FOR x = 0 TO 640
         if Dref= 4 then y = 50 * SIN((x - MASRrefLAT) / 101.859164#) else y = 80 * sin((x - 10) / 101.859164#)
         LINE (x - 1, 159 - y)-(x + 1, 161 - y), 15, BF
        NEXT x
        LATtarg = 80 * SIN((LONGtarg - 10) / 101.859164#)
        if Dref=4 then y = 50 * SIN((LONGtarg - MASRrefLAT) / 101.859164#)
        CIRCLE (LONGtarg, 160 - LATtarg), 1, 13

        'Drawn latitude and longitude lines
100     FOR x = 0 TO 640 STEP 53.333
         LINE (x, 0)-(x, 319), 7
        NEXT x
        FOR y = 0 TO 319 STEP 53.333
         LINE (0, y)-(640, y), 7
        NEXT y
        LINE (0, 319)-(640, 319), 7




200     GOSUB 800
        LOCATE 21, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 21, 64
        COLOR 11: PRINT USING "####"; year;
        PRINT ":"; : PRINT USING "###"; day;
        PRINT ":"; : PRINT USING "##"; HR;
        PRINT ":"; : PRINT USING "##"; min;
        PRINT ":"; : PRINT USING "##"; sec;
        MET# = (year * 31536000#) + (day * 86400#) + (HR * 3600#) + (min * 60#) + sec
        IF MET# > MST# THEN MET# = MET# - MST#: METsgn = 1 ELSE MET# = MST# - MET#: METsgn = -1
        METyear# = INT(MET# / 31536000#)
        METday# = MET# - (METyear# * 31536000#)
        METday# = INT(METday# / 86400#)
        METhr# = MET# - (METyear# * 31536000#) - (METday# * 86400#)
        METhr# = INT(METhr# / 3600#)
        METmin# = MET# - (METyear# * 31536000#) - (METday# * 86400#) - (METhr# * 3600#)
        METmin# = INT(METmin# / 60#)
        METsec# = MET# - (METyear# * 31536000#) - (METday# * 86400#) - (METhr# * 3600#) - (METmin# * 60#)
       
        LOCATE 22, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 23, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 23, 60: COLOR 9: PRINT "MET:  ";
        COLOR 11 - METsgn
        LOCATE 24, 63
        IF METsgn = -1 THEN PRINT "-";  ELSE PRINT " ";
        LOCATE 23, 64
        PRINT USING "####"; METyear#;
        PRINT ":"; : PRINT USING "###"; METday#;
        PRINT ":"; : PRINT USING "##"; METhr#;
        PRINT ":"; : PRINT USING "##"; METmin#;
        PRINT ":"; : PRINT USING "##"; METsec#;
               
        MSTyear# = INT(MST# / 31536000#)
        MSTday# = MST# - (MSTyear# * 31536000#)
        MSTday# = INT(MSTday# / 86400#)
        MSThr# = MST# - (MSTyear# * 31536000#) - (MSTday# * 86400#)
        MSThr# = INT(MSThr# / 3600#)
        MSTmin# = MST# - (MSTyear# * 31536000#) - (MSTday# * 86400#) - (MSThr# * 3600#)
        MSTmin# = INT(MSTmin# / 60#)
        MSTsec# = MST# - (MSTyear# * 31536000#) - (MSTday# * 86400#) - (MSThr# * 3600#) - (MSTmin# * 60#)
       
        LOCATE 24, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 24, 60: COLOR 9: PRINT "MST:  ";
        LOCATE 24, 64
        COLOR 11: PRINT USING "####"; MSTyear#;
        PRINT ":"; : PRINT USING "###"; MSTday#;
        PRINT ":"; : PRINT USING "##"; MSThr#;
        PRINT ":"; : PRINT USING "##"; MSTmin#;
        PRINT ":"; : PRINT USING "##"; MSTsec#;

        LOCATE 25, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 26, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 27, 59: COLOR 8: PRINT CHR$(186);
        LOCATE 28, 59: COLOR 8: PRINT CHR$(186);
       
        EET# = (year * 31536000#) + (day * 86400#) + (HR * 3600#) + (min * 60#) + sec
        IF EET# > EST# THEN EET# = EET# - EST#: EETsgn = 1 ELSE EET# = EST# - EET#: EETsgn = -1
        EETyear# = INT(EET# / 31536000#)
        EETday# = EET# - (EETyear# * 31536000#)
        EETday# = INT(EETday# / 86400#)
        EEThr# = EET# - (EETyear# * 31536000#) - (EETday# * 86400#)
        EEThr# = INT(EEThr# / 3600#)
        EETmin# = EET# - (EETyear# * 31536000#) - (EETday# * 86400#) - (EEThr# * 3600#)
        EETmin# = INT(EETmin# / 60#)
        EETsec# = EET# - (EETyear# * 31536000#) - (EETday# * 86400#) - (EEThr# * 3600#) - (EETmin# * 60#)
        ESTyear# = INT(EST# / 31536000#)
        ESTday# = EST# - (ESTyear# * 31536000#)
        ESTday# = INT(ESTday# / 86400#)
        ESThr# = EST# - (ESTyear# * 31536000#) - (ESTday# * 86400#)
        ESThr# = INT(ESThr# / 3600#)
        ESTmin# = EST# - (ESTyear# * 31536000#) - (ESTday# * 86400#) - (ESThr# * 3600#)
        ESTmin# = INT(ESTmin# / 60#)
        ESTsec# = EST# - (ESTyear# * 31536000#) - (ESTday# * 86400#) - (ESThr# * 3600#) - (ESTmin# * 60#)
       
        LOCATE 26, 60: COLOR 9: PRINT "EET:";
        COLOR 11 - EETsgn
        PRINT USING "####"; EETyear#;
        PRINT ":"; : PRINT USING "###"; EETday#;
        PRINT ":"; : PRINT USING "##"; EEThr#;
        PRINT ":"; : PRINT USING "##"; EETmin#;
        PRINT ":"; : PRINT USING "##"; EETsec#;
        LOCATE 27, 60: COLOR 9: PRINT "EST:";
        COLOR 11: PRINT USING "####"; ESTyear#;
        PRINT ":"; : PRINT USING "###"; ESTday#;
        PRINT ":"; : PRINT USING "##"; ESThr#;
        PRINT ":"; : PRINT USING "##"; ESTmin#;
        PRINT ":"; : PRINT USING "##"; ESTsec#;

        




        GOSUB 300
        x1 = 640 * (Ahab + 59.25 + 180) / 360
        IF x1 > 640 THEN x1 = x1 - 640
        if Dref = 4 then y1 = 50 * SIN((x1 - MASRrefLAT) / 101.859164#) else y1 = 80 * sin((x1 - 10) / 101.859164#)
        IF Dhab > 10000000 THEN y1 = y1 * 10000000 / Dhab
        if Dref=4 then gosub 5000 else locate 28,1:print space$(18);:goto 299
            color 9
            locate 28, 1:print "ELEV:            m";
            color 11
            locate 28, 10:print using "######.#";h;

        'if MARSmag=0 then LINE (x1 - 1, 159 - y1)-(x1 + 1, 161 - y1), 12, BF: PSET (x1, 160 - y1), 14
        'if MARSmag=1 then xMAG=(x1*5)-MAPcornerX:yMAG=(y1*5)-MAPcornerY: LINE (xMAG - 1, 159 - yMAG)-(xMAG + 1, 161 - yMAG), 12, BF: PSET (xMAG, 160 - yMAG), 14
299     COLOR 14: LOCATE 21, 1: PRINT nme$(Dref); 'SPACE$(8 - LEN(nme$(Dref))); Dref; filename4$;
        LOCATE 22, 1: COLOR 9: PRINT "LONG:  "; : COLOR 11: PRINT USING "########.#"; ABS((x1 * 57.29578 / 101.859164#) - 180); : COLOR 9: IF x1 < 320 THEN PRINT "W";  ELSE PRINT "E";
        LOCATE 23, 1: COLOR 9: PRINT "LAT:   "; : COLOR 11: PRINT USING "########.#"; (ABS(y1) * 57.29578 / 101.859164#); : COLOR 9: IF y1 < 0 THEN PRINT "S";  ELSE PRINT "N";
        LOCATE 24, 1: COLOR 9: PRINT "ANGLE: "; : COLOR 11: PRINT USING "########.#"; (Ahab); : COLOR 9: PRINT CHR$(248);
        LOCATE 25, 1: COLOR 9: PRINT "ALT:   "; : COLOR 11:
        IF (Dhab - P(28, 5) - P(Dref, 5)) > 9999999900# THEN PRINT USING "########.#"; (Dhab - P(28, 5) - P(Dref, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "########.#"; (Dhab - P(28, 5) - P(Dref, 5)) / 1000; : COLOR 9: PRINT "km";
        LOCATE 26, 1: COLOR 9: PRINT "ENGINE:"; : COLOR 11: PRINT USING "########.#"; eng; : COLOR 9: PRINT "%";
        LOCATE 27, 1: COLOR 9: PRINT "NAV:   "; : COLOR 11
          IF Sflag = 0 THEN PRINT "  ccw prog "; : GOTO 201
          IF Sflag = 4 THEN PRINT "  ccw retro"; : GOTO 201
          IF Sflag = 1 THEN PRINT "  manual   "; : GOTO 201
          IF Sflag = 2 THEN PRINT "  app targ "; : GOTO 201
          IF Sflag = 3 THEN PRINT "  dep ref  ";
        

201     x2 = 640 * (Aayse + 59.25 + 180) / 360
        IF x2 > 640 THEN x2 = x2 - 640
        if Dref = 4 then y2 = 50 * SIN((x2 - MASRrefLAT) / 101.859164#) else y2 = 80 * SIN((x2 - 10) / 101.859164#)
        IF Dayse > 10000000 THEN y2 = y2 * 10000000 / Dayse
        IF Dayse < 100000000 THEN LINE (x2 - 1, 159 - y2)-(x2 + 1, 161 - y2), 6, BF
       
        x3 = 640 * (Aiss + 59.25 + 180) / 360
        IF x3 > 640 THEN x3 = x3 - 640
        y3 = 80 * SIN((x3 - 10) / 101.859164#)
        IF Diss > 10000000 THEN y3 = y3 * 10000000 / Diss
        IF Diss < 100000000 THEN LINE (x3 - 1, 159 - y3)-(x3 + 1, 161 - y3), 4, BF
        
        IF Dufo1 > 10000000 THEN 221
        x4 = 640 * (Aufo1 + 59.25 + 180) / 360
        IF x4 > 640 THEN x4 = x4 - 640
        y4 = 80 * SIN((x4 - 10) / 101.859164#)
        IF Dufo1 > 10000000 THEN y4 = y4 * 10000000 / Dufo1
        IF Dufo1 < 100000000 THEN LINE (x4 - 1, 159 - y4)-(x4 + 1, 161 - y4), 13, BF

221     x6 = 640 * (Aocess + 59.25 + 180) / 360
        IF x6 > 640 THEN x6 = x6 - 640
        y6 = 80 * SIN((x6 - 10) / 101.859164#)
        IF Docess > 10000000 THEN y6 = y6 * 10000000 / Docess
        IF Docess < 100000000 THEN LINE (x6 - 2, 158 - y6)-(x6 + 2, 162 - y6), 10, B

230     IF MODULEflag = 0 THEN 240
        x5 = 640 * (Amod + 59.25 + 180) / 360
        IF x5 > 640 THEN x5 = x5 - 640
        y5 = 80 * SIN((x5 - 10) / 101.859164#)
        IF Dmod > 10000000 THEN y5 = y5 * 10000000 / Dmod
        IF Dmod < 100000000 THEN LINE (x5 - 1, 159 - y5)-(x5 + 1, 161 - y5), 2, BF

240     LOCATE 21, 21: COLOR 8: PRINT CHR$(186); : COLOR 6: PRINT "AYSE: ";
        COLOR 11
        IF (Dhabayse - P(28, 5) - P(32, 5)) > 999999000# THEN PRINT USING "#######"; (Dhabayse - P(28, 5) - P(32, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabayse - P(28, 5) - P(32, 5)) / 1000; : COLOR 9: PRINT "km";
        LOCATE 21, 37: COLOR 11
        IF (Dayse - P(32, 5) - P(Dref, 5)) > 999999000# THEN PRINT USING "#######"; (Dayse - P(32, 5) - P(Dref, 5)) / 1000000; : COLOR 9: PRINT "Mm alt";  ELSE PRINT USING "#######"; (Dayse - P(32, 5) - P(Dref, 5)) / 1000; : COLOR 9: PRINT "km alt"; _

        delA = ABS(Ahab - Aayse)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 21, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);
       
        LOCATE 22, 21: COLOR 8: PRINT CHR$(186);
        COLOR 4: PRINT "ISS:  ";
        COLOR 11
        IF (Dhabiss - P(28, 5) - P(35, 5)) > 9999999000# THEN PRINT USING "#######"; (Dhabiss - P(28, 5) - P(35, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabiss - P(28, 5) - P(35, 5)) / 1000; : COLOR 9: PRINT "km";
        LOCATE 22, 37: COLOR 11
        IF (Diss - P(35, 5) - P(Dref, 5)) > 9999999000# THEN PRINT USING "#######"; (Diss - P(35, 5) - P(Dref, 5)) / 1000000; : COLOR 9: PRINT "Mm alt";  ELSE PRINT USING "#######"; (Diss - P(35, 5) - P(Dref, 5)) / 1000; : COLOR 9: PRINT "km alt";
        delA = ABS(Ahab - Aiss)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 22, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);


205     LOCATE 24, 21: COLOR 8: PRINT CHR$(186);
        COLOR 14: LOCATE 24, 29: PRINT SPACE$(8 - LEN(nme$(targ))); nme$(targ);
        LOCATE 23, 21: COLOR 8: PRINT CHR$(186); : COLOR 9: PRINT "TARG: ";
        COLOR 11
        IF (Dhabtarg - P(28, 5) - P(targ, 5)) > 9999999000# THEN PRINT USING "#######"; (Dhabtarg - P(28, 5) - P(targ, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabtarg - P(28, 5) - P(targ, 5)) / 1000; : COLOR 9: PRINT  _
"km";
        LOCATE 23, 37: COLOR 11
        IF targ = Dref THEN PRINT SPACE$(20): GOTO 214
        IF (Dtarg - P(targ, 5) - P(Dref, 5)) > 9999999000# THEN PRINT USING "#######"; (Dtarg - P(targ, 5) - P(Dref, 5)) / 1000000; : COLOR 9: PRINT "Mm alt";  ELSE PRINT USING "#######"; (Dtarg - P(targ, 5) - P(Dref, 5)) / 1000; : COLOR 9: PRINT  _
"km alt";
        delA = ABS(Ahab - Atarg)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 23, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);
214     LOCATE 25, 21: COLOR 8: PRINT CHR$(186);
        COLOR 14: PRINT "LAND:";
        x7 = 640 * (LONGtarg + 59.25 + 180) / 360
        IF x7 > 640 THEN x7 = x7 - 640
        y7 = 80 * SIN((x7 - 10) / 101.859164#)
        if Dref = 4 then y7 = 50 * SIN((x7 - MASRrefLAT) / 101.859164#)
        delA = ABS(Ahab - LONGtarg)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 25, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);
        LOCATE 25, 28: COLOR 11: PRINT USING "###.###"; ABS((x7 * 57.29578 / 101.859164#) - 180); : COLOR 9: IF x7 < 320 THEN PRINT "W";  ELSE PRINT "E";
        LOCATE 25, 37: COLOR 11: PRINT USING "###.###"; (ABS(y7) * 57.29578 / 101.859164#); : COLOR 9: IF y7 < 0 THEN PRINT "S";  ELSE PRINT "N";
        

  
204     LOCATE 28, 21: COLOR 8: PRINT CHR$(186);
        IF Dufo1 > 100000000 THEN PRINT SPACE$(35); : GOTO 208
        COLOR 13: PRINT "UFO:  ";
        COLOR 11
        IF (Dhabufo1 - P(38, 5) - P(28, 5)) > 999999000# THEN PRINT USING "#######"; (Dhabufo1 - P(28, 5) - P(38, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabufo1 - P(28, 5) - P(38, 5)) / 1000; : COLOR 9: PRINT "km";
        LOCATE 28, 37: COLOR 11
        IF (Dufo1 - P(28, 5) - P(Dref, 5)) > 999999000# THEN PRINT USING "#######"; (Dufo1 - P(38, 5) - P(Dref, 5)) / 1000000; : COLOR 9: PRINT "Mm alt";  ELSE PRINT USING "#######"; (Dufo1 - P(38, 5) - P(Dref, 5)) / 1000; : COLOR 9: PRINT "km alt"; _

        delA = ABS(Ahab - Aufo1)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 28, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);


208     LOCATE 27, 21: COLOR 8: PRINT CHR$(186);
        COLOR 2: PRINT "MOD:  ";
        COLOR 11
        IF (Dhabmod - P(28, 5) - P(36, 5)) > 999999000# THEN PRINT USING "#######"; (Dhabmod - P(28, 5) - P(36, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabmod - P(28, 5) - P(36, 5)) / 1000; : COLOR 9: PRINT "km";
        delA = ABS(Ahab - Amod)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 27, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);


207     LOCATE 26, 21: COLOR 8: PRINT CHR$(186);
        'IF Dhabocess > 100000000 THEN PRINT SPACE$(35); : GOTO 203
        COLOR 10: PRINT "OCESS:";
        COLOR 11
        IF (Dhabocess - P(37, 5) - P(28, 5)) > 999999000# THEN PRINT USING "#######"; (Dhabocess - P(28, 5) - P(37, 5)) / 1000000; : COLOR 9: PRINT "Mm";  ELSE PRINT USING "#######"; (Dhabocess - P(28, 5) - P(37, 5)) / 1000; : COLOR 9: PRINT "km";
        delA = ABS(Ahab - Aocess)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 26, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);
203     COLOR 7


209     tt = TIMER
        ttt = TIMER
210     z$ = INKEY$
        'locate 1,60:print setflag;
        IF z$ = "Q" THEN END
        IF z$ = CHR$(27) THEN END
       
        LONGtargUPDATE = 0
        LONGtargdel = 1
        if MAGmars=1 then LONGtargdel=.2
        if MAGmars=2 then LONGtargdel=.05
        if MAGmars=3 then LONGtargdel=0.005
        IF z$ = CHR$(0) + "M" THEN LONGtargUPDATE = 1: LONGtarg = LONGtarg + LONGtargdel: IF LONGtarg > 360 THEN LONGtarg = LONGtarg - 360
        IF z$ = CHR$(0) + "K" THEN LONGtargUPDATE = 1: LONGtarg = LONGtarg - LONGtargdel: IF LONGtarg < 0 THEN LONGtarg = LONGtarg + 360
        IF LONGtargUPDATE = 0 THEN 211
        'CIRCLE (x7, 160 - y7), 1, 15
        if MAGmars=0 then CIRCLE (x7, 160 - y7), 1, 15
        if MAGmars=1 then xMAG=(x7*5)-MAPcornerX:yMAG=((y7+160)*5)-MAPcornerY: circle (xMAG, 320-yMAG),1, 15
        if MAGmars=2 then xMAG=(x7*18)-MAPcornerX:yMAG=((y7+160)*18)-MAPcornerY: circle (xMAG, 320-yMAG),1, 15
        if MAGmars=3 then xMAG=((x7*18)-MAPcornerX)*10:yMAG=(((y7+160)*18)-MAPcornerY)*10: circle (xMAG, 320-yMAG),1, 15

        x7 = 640 * (LONGtarg + 59.25 + 180) / 360
        IF x7 > 640 THEN x7 = x7 - 640
        y7 = 80 * SIN((x7 - 10) / 101.859164#)
        if Dref = 4 then y7 = 50 * SIN((x7 - MASRrefLAT) / 101.859164#)
        if Dref = 4 then gosub 5050 else locate 24, 49:print "         ";: goto 298
            color 11
            locate 24, 49:print using "######.#";h;
            color 9:print "m";
            z$=input$(1)


        'LOCATE 25, 28: COLOR 11: PRINT USING "#######"; LONGtarg;
298     delA = ABS(Ahab - LONGtarg)
        IF delA > 180 THEN delA = 360 - delA
        COLOR 11
        LOCATE 25, 51
        PRINT USING "####.#"; delA;
        COLOR 9: PRINT CHR$(248);
        LOCATE 25, 28: COLOR 11: PRINT USING "###.###"; ABS((x7 * 57.29578 / 101.859164#) - 180); : COLOR 9: IF x7 < 320 THEN PRINT "W";  ELSE PRINT "E";
        LOCATE 25, 37: COLOR 11: PRINT USING "###.###"; (ABS(y7) * 57.29578 / 101.859164#); : COLOR 9: IF y7 < 0 THEN PRINT "S";  ELSE PRINT "N";


       
211     'IF z$ = CHR$(9) THEN 90
        IF z$ = "s" THEN z$ = ""
        IF z$ = "w" THEN z$ = ""
        'if z$ = "|" then setflag=1:beep   ':gosub 5050:setflag=0':goto 90
        if Dref <> 4 then 219
        if z$ = "*" then VIEWcentre=1-VIEWcentre:goto 90
        if z$ <> "+" then 218
            MAGmars=MAGmars+1
            if MAGmars>3 then MAGmars=3
            goto 90
218     if z$ <> "-" then 219
            MAGmars=MAGmars-1
            if MAGmars<0 then MAGmars=0
            goto 90
        'IF z$ = CHR$(0) + "?" AND Dref = 33 THEN filename4$ = "thermal.bmp": GOTO 90
        'IF z$ = CHR$(0) + "@" AND Dref = 33 THEN filename4$ = "magnetic.bmp": GOTO 90
        'IF z$ = CHR$(0) + "A" AND Dref = 33 THEN filename4$ = "moist.bmp": GOTO 90
        'IF Dref <> 33 THEN filename4$ = ""
219     IF z$ > "/" AND z$ < ":" THEN Dref = VAL(z$): GOTO 90
        IF z$ >= "a" AND z$ < "z" THEN Dref = ASC(z$) - 87: GOTO 90
        IF UCASE$(z$) = "C" THEN 91
        IF z$ = CHR$(0) + CHR$(134) THEN flag = 25: GOSUB 700
        IF z$ = CHR$(0) + CHR$(133) THEN flag = 28: GOSUB 700
        IF TIMER - ttt > .5 THEN st1 = 1 - st1: ttt = TIMER
        IF Dayse >= 100000000 THEN 217
        if MAGmars = 0 then LINE (x2 - 1, 159 - y2)-(x2 + 1, 161 - y2), (6 * st1) + (15 * (1 - st1)), BF
        if MAGmars=1 then xMAG=(x2*5)-MAPcornerX:yMAG=((y2+160)*5)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (6 * st1) + (15 * (1 - st1)), BF
        if MAGmars=2 then xMAG=(x2*18)-MAPcornerX:yMAG=((y2+160)*18)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (6 * st1) + (15 * (1 - st1)), BF
        if MAGmars=3 then xMAG=((x2*18)-MAPcornerX)*10:yMAG=(((y2+160)*18)-MAPcornerY)*10: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (6 * st1) + (15 * (1 - st1)), BF

217     if Dref<>3 then 276
        IF Docess < 100000000 THEN LINE (x6 - 2, 158 - y6)-(x6 + 2, 162 - y6), (0 * st1) + (15 * (1 - st1)), B
        IF Diss < 100000000 THEN LINE (x3 - 1, 159 - y3)-(x3 + 1, 161 - y3), (4 * st1) + (15 * (1 - st1)), BF
276     IF Dmod < 100000000 THEN LINE (x5 - 1, 159 - y5)-(x5 + 1, 161 - y5), (2 * st1) + (15 * (1 - st1)), BF
        IF Dufo1 < 100000000 THEN LINE (x4 - 1, 159 - y4)-(x4 + 1, 161 - y4), (13 * st1) + (15 * (1 - st1)), BF
        

        if MAGmars=0 then LINE (x1 - 1, 159 - y1)-(x1 + 1, 161 - y1), (12 * st1) + (15 * (1 - st1)), BF
        if MAGmars=1 then xMAG=(x1*5)-MAPcornerX:yMAG=((y1+160)*5)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (12 * st1) + (15 * (1 - st1)), BF
        if MAGmars=2 then xMAG=(x1*18)-MAPcornerX:yMAG=((y1+160)*18)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (12 * st1) + (15 * (1 - st1)), BF
        if MAGmars=3 then xMAG=((x1*18)-MAPcornerX)*10:yMAG=(((y1+160)*18)-MAPcornerY)*10: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), (12 * st1) + (15 * (1 - st1)), BF
        if MAGmars=0 then CIRCLE (x7, 160 - y7), 1, (1 * st1) + (15 * (1 - st1))
        if MAGmars=1 then xMAG=(x7*5)-MAPcornerX:yMAG=((y7+160)*5)-MAPcornerY: circle (xMAG, 320-yMAG),1, (12 * st1) + (15 * (1 - st1))
        if MAGmars=2 then xMAG=(x7*18)-MAPcornerX:yMAG=((y7+160)*18)-MAPcornerY: circle (xMAG, 320-yMAG),1, (12 * st1) + (15 * (1 - st1))
        if MAGmars=3 then xMAG=((x7*18)-MAPcornerX)*10:yMAG=(((y7+160)*18)-MAPcornerY)*10: circle (xMAG, 320-yMAG),1, (12 * st1) + (15 * (1 - st1))


        IF TIMER - tt < 2 THEN 210
        if MAGmars=0 then LINE (x1 - 1, 159 - y1)-(x1 + 1, 161 - y1), 15, BF
        if MAGmars=1 then xMAG=(x1*5)-MAPcornerX:yMAG=((y1+160)*5)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF
        if MAGmars=2 then xMAG=(x1*18)-MAPcornerX:yMAG=((y1+160)*18)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF
        if MAGmars=3 then xMAG=((x1*18)-MAPcornerX)*10:yMAG=(((y1+160)*18)-MAPcornerY)*10: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF

'        LINE (x1 - 1, 159 - y1)-(x1 + 1, 161 - y1), 15, BF
        IF Dayse >= 100000000 THEN 297
        if MAGmars=0 then LINE (x2 - 1, 159 - y2)-(x2 + 1, 161 - y2), 15, BF
        if MAGmars=1 then xMAG=(x2*5)-MAPcornerX:yMAG=((y2+160)*5)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF
        if MAGmars=2 then xMAG=(x2*18)-MAPcornerX:yMAG=((y2+160)*18)-MAPcornerY: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF
        if MAGmars=3 then xMAG=((x2*18)-MAPcornerX)*10:yMAG=(((y2+160)*18)-MAPcornerY)*10: LINE (xMAG - 1, 320-yMAG-1)-(xMAG + 1, 320-yMAG+1), 15, BF

297     IF Diss < 100000000 and Dref=3 THEN LINE (x3 - 1, 159 - y3)-(x3 + 1, 161 - y3), 15, BF
        IF Dufo1 < 100000000 THEN LINE (x4 - 1, 159 - y4)-(x4 + 1, 161 - y4), 15, BF
        IF Dmod < 100000000 THEN LINE (x5 - 1, 159 - y5)-(x5 + 1, 161 - y5), 15, BF
        GOSUB 790
        GOTO 200

       
       
        'SUBROUTINE: Calculate orbit parameters
300     difx = Px(28, 3) - Px(Dref, 3)
        dify = Py(28, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Dhab = R
        Ahab = angle * 57.29578

        difx = Px(32, 3) - Px(Dref, 3)
        dify = Py(32, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Dayse = R
        Aayse = angle * 57.29578
        difx = Px(32, 3) - Px(28, 3)
        dify = Py(32, 3) - Py(28, 3)
        Dhabayse = SQR((dify ^ 2) + (difx ^ 2))
       
        difx = Px(35, 3) - Px(Dref, 3)
        dify = Py(35, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Aiss = angle * 57.29578
        Diss = R
        difx = Px(35, 3) - Px(28, 3)
        dify = Py(35, 3) - Py(28, 3)
        Dhabiss = SQR((dify ^ 2) + (difx ^ 2))

        difx = Px(targ, 3) - Px(Dref, 3)
        dify = Py(targ, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Atarg = angle * 57.29578
        Dtarg = R
        IF targ = Dref THEN Dtarg = 2 * (P(targ, 5))
        difx = Px(targ, 3) - Px(28, 3)
        dify = Py(targ, 3) - Py(28, 3)
        Dhabtarg = SQR((dify ^ 2) + (difx ^ 2))
       


        IF Px(38, 3) = 0 THEN Dufo1 = 9999999999#: GOTO 350
        difx = Px(38, 3) - Px(Dref, 3)
        dify = Py(38, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Dufo1 = R
        Aufo1 = angle * 57.29578
        difx = Px(38, 3) - Px(28, 3)
        dify = Py(38, 3) - Py(28, 3)
        Dhabufo1 = SQR((dify ^ 2) + (difx ^ 2))

350     IF Px(39, 3) = 0 THEN Dufo2 = 9999999999#: GOTO 360
        difx = Px(39, 3) - Px(Dref, 3)
        dify = Py(39, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Dufo2 = R
        Aufo2 = angle * 57.29578
        difx = Px(39, 3) - Px(28, 3)
        dify = Py(39, 3) - Py(28, 3)
        Dhabufo2 = SQR((dify ^ 2) + (difx ^ 2))

360     IF MODULEflag = 0 THEN Dmod = 9999999999999#: Amod = Ahab: GOTO 370
        difx = Px(36, 3) - Px(Dref, 3)
        dify = Py(36, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Dmod = R
        Amod = angle * 57.29578
        difx = Px(28, 3) - Px(36, 3)
        dify = Py(28, 3) - Py(36, 3)
        Dhabmod = SQR((dify ^ 2) + (difx ^ 2))

370     difx = Px(37, 3) - Px(Dref, 3)
        dify = Py(37, 3) - Py(Dref, 3)
        R = SQR((dify ^ 2) + (difx ^ 2))
        IF dify = 0 THEN IF difx < 0 THEN angle = .5 * 3.1415926535# ELSE angle = 1.5 * 3.1415926535# ELSE angle = ATN(difx / dify)
        IF dify > 0 THEN angle = angle + 3.1415926535#
        IF difx > 0 AND dify < 0 THEN angle = angle + 6.283185307#
        Docess = R
        Aocess = angle * 57.29578
        difx = Px(37, 3) - Px(28, 3)
        dify = Py(37, 3) - Py(28, 3)
        Dhabocess = SQR((dify ^ 2) + (difx ^ 2))
        RETURN



700     IF flag = 25 THEN M# = MST# ELSE M# = EST#
        MSTy# = INT(M# / 31536000#)
        MSTd# = M# - (MSTy# * 31536000#)
        MSTd# = INT(MSTd# / 86400#)
        MSTh# = M# - (MSTy# * 31536000#) - (MSTd# * 86400#)
        MSTh# = INT(MSTh# / 3600#)
        MSTm# = M# - (MSTy# * 31536000#) - (MSTd# * 86400#) - (MSTh# * 3600#)
        MSTm# = INT(MSTm# / 60#)
        MSTs# = M# - (MSTy# * 31536000#) - (MSTd# * 86400#) - (MSTh# * 3600#) - (MSTm# * 60#)

        LOCATE flag, 64: PRINT "year:         ";
        LOCATE flag, 70: INPUT ; "", z$
        IF z$ <> "" THEN MSTy# = VAL(z$)
        IF MSTy# < 0 THEN MSTy# = 0
        MSTy# = INT(MSTy#)
        M# = MSTy# * 31536000#
       
        LOCATE flag, 64: PRINT "day:          ";
        LOCATE flag, 69: INPUT ; "", z$
        IF z$ <> "" THEN MSTd# = VAL(z$)
        IF MSTd# < 1 THEN MSTd# = 1
        IF MSTd# > 365 THEN MSTd# = 365
        MSTd# = INT(MSTd#)
        M# = M# + (MSTd# * 86400#)
       
        LOCATE flag, 64: PRINT "hour:         ";
        LOCATE flag, 70: INPUT ; "", z$
        IF z$ <> "" THEN MSTh# = VAL(z$)
        IF MSTh# < 0 THEN MSTh# = 0
        IF MSTh# > 23 THEN MSTh# = 23
        MSTh# = INT(MSTh#)
        M# = M# + (MSTh# * 3600#)
       
        LOCATE flag, 64: PRINT "min:          ";
        LOCATE flag, 69: INPUT ; "", z$
        IF z$ <> "" THEN MSTm# = VAL(z$)
        IF MSTm# < 0 THEN MSTm# = 0
        IF MSTm# > 59 THEN MSTm# = 59
        MSTm# = INT(MSTm#)
        M# = M# + (MSTm# * 60#)
       
        LOCATE flag, 64: PRINT "sec:          ";
        LOCATE flag, 69: INPUT ; "", z$
        IF z$ <> "" THEN MSTs# = VAL(z$)
        IF MSTs# < 0 THEN MSTs# = 0
        IF MSTs# > 59 THEN MSTs# = 59
        MSTs# = INT(MSTs#)
        LOCATE flag, 64: PRINT "              ";
        M# = M# + MSTs#
        IF flag = 25 THEN MST# = M# ELSE EST# = M#
        RETURN


790     OPEN "R", #1, "MST.RND", 26
        chkBYTE=chkBYTE+1
        if chkBYTE>58 then chkBYTE=1
        outSTR$ = chr$(chkBYTE+64)
        outSTR$ = outSTR$ + mkd$(MST#)
        outSTR$ = outSTR$ + mkd$(EST#)
        outSTR$ = outSTR$ + mkd$(LONGtarg)
        outSTR$ = outSTR$ + chr$(chkBYTE+64)
        Put #1, 1, outSTR$
        close #1
        return
        
        
        

        'SUBROUTINE: Timed telemetry retrieval
800     
k=1
        locate 22, 64: print "           ";
802     OPEN "R", #1, "OSBACKUP.RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if len(inpSTR$) <> 1427 then color 12,0: locate 22, 64: print "TELEM ERROR";:return
        IF left$(ORBITversion$,5) = "XXXXX" THEN RUN "orbit5vd"
        IF ORBITversion$ <> "ORBIT5S" THEN color 12,0: locate 22, 64: print "TELEM ERROR";:return
        if chkCHAR1$=chkCHAR2$ then 807
        k=k+1
        if k<4 then 802
        color 12,0: locate 22, 64: print "TELEM ERROR";:return
        
807     k=2+15
        eng = cvs(mid$(inpSTR$,k,4)):k=k+8
        Sflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        k=k+62
        year = cvi(mid$(inpSTR$,k,2)):k=k+2
        day = cvi(mid$(inpSTR$,k,2)):k=k+2
        hr = cvi(mid$(inpSTR$,k,2)):k=k+2
        min = cvi(mid$(inpSTR$,k,2)):k=k+2
        sec = cvd(mid$(inpSTR$,k,8)):k=k+8
        k=k+24
        MODULEflag = cvi(mid$(inpSTR$,k,2)):k=k+2
        AYSEdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        OCESSdist = cvs(mid$(inpSTR$,k,4)):k=k+4
        k=k+24
        pressure = cvs(mid$(inpSTR$,k,4)):k=k+4
        Accel# = cvs(mid$(inpSTR$,k,4)):k=k+4
        FOR i = 1 TO 39
         Px(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+8
         Py(i, 3) = cvd(mid$(inpSTR$,k,8)):k=k+24
        NEXT i
        fuel = cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEfuel = cvs(mid$(inpSTR$,k,4)):k=k+4
        Px(0, 3) = 0
        Py(0, 3) = 0
        Px(37, 3) = 4446370.8284487# + Px(3, 3): Py(37, 3) = 4446370.8284487# + Py(3, 3)
        RETURN

3000    'IF ERL = 800 THEN RESUME 802
        'IF ERL = 801 THEN RESUME 802
        color 12, 0
        LOCATE 28, 22: PRINT "ERROR: line"; ERL;" #"; ERR;
        z$ = INPUT$(1)
        END


4000
        GOSUB 300
        x1 = 640 * (Ahab + 59.25 + 180) / 360
        IF x1 > 640 THEN x1 = x1 - 640
        y1 = 50 * SIN((x1 - MASRrefLAT) / 101.859164#)
        lng=  ABS((x1 * 57.29578 / 101.859164#))
        lat = (y1 * 57.29578 / 101.859164#) + 90
        if VIEWcentre=0 then 4001
        lng=(x7 * 57.29578 / 101.859164#)
        lat=(y7 * 57.29578 / 101.859164#)+90


4001
        MAPx=lng*3200/360
        MAPy=lat*1600/180
        MAPx=cint(MAPx)
        MAPy=cint(MAPy)
        MAPcornerX = MAPx-320: if MAPcornerX<1 then MAPcornerX=1
        MAPcornerY = MAPY-160: if MAPcornerY<1 then MAPcornerY=1
        MAPupcornerX=MAPcornerX+640: if MAPupcornerX>3200 then MAPcornerX=2560:MAPupcornerX=3200
        MAPupcornerY=MAPcornerY+320: if MAPupcornerY>1600 then MAPcornerY=1280:MAPupcornerY=1600

'print MAPx
'print MAPy
'print MAPcornerX
'print MAPcornerY
'print MAPupcornerX
'print MAPupcornerY
'z$=input$(1)
'cls
        open "R", #1, "marsMDa.bmp",1
        a$ = " " 
'1079
'for i=1 to 10000000
        for i=MAPcornerY to MAPupcornerY
            for j=MAPcornerX to MAPupcornerX
                l=((i-1)*3200)+j+1078
                get #1, l, a$
                c=asc(a$)
                pset (j-MAPcornerX,320-(i-MAPcornerY)-1),c
            next j
        next i
        close #1
        return
        
4100
        GOSUB 300
        x1 = 640 * (Ahab + 59.25 + 180) / 360
        IF x1 > 640 THEN x1 = x1 - 640
        y1 = 50 * SIN((x1 - MASRrefLAT) / 101.859164#)
        lng=  ABS((x1 * 57.29578 / 101.859164#))
        lat = (y1 * 57.29578 / 101.859164#) + 90
        if VIEWcentre=0 then 4101
        lng=(x7 * 57.29578 / 101.859164#)
        lat=(y7 * 57.29578 / 101.859164#)+90


4101


        MAPx=lng*11520/360
        MAPy=lat*5760/180
        MAPx=cint(MAPx)
        MAPy=cint(MAPy)
        MAPcornerX = MAPx-320: if MAPcornerX<1 then MAPcornerX=1
        MAPcornerY = MAPY-160: if MAPcornerY<1 then MAPcornerY=1
        MAPupcornerX=MAPcornerX+640: if MAPupcornerX>11520 then MAPcornerX=10880:MAPupcornerX=11520
        MAPupcornerY=MAPcornerY+320: if MAPupcornerY>5760 then MAPcornerY=5440:MAPupcornerY=5760

        open "R", #1, "marsLGa.bmp",1
        a$ = " " 
'1079
'for i=1 to 10000000
        for i=MAPcornerY to MAPupcornerY
            for j=MAPcornerX to MAPupcornerX
                l=((i-1)*11520)+j+1078
                get #1, l, a$
                c=asc(a$)
                pset (j-MAPcornerX,320-(i-MAPcornerY)-1),c
            next j
        next i
        close #1
        return
        
        
4200
        GOSUB 300
        x1 = 640 * (Ahab + 59.25 + 180) / 360
        IF x1 > 640 THEN x1 = x1 - 640
        y1 = 50 * SIN((x1 - MASRrefLAT) / 101.859164#)
        lng=  ABS((x1 * 57.29578 / 101.859164#))
        lat = (y1 * 57.29578 / 101.859164#) + 90
        if VIEWcentre=0 then 4201
        lng=(x7 * 57.29578 / 101.859164#)
        lat=(y7 * 57.29578 / 101.859164#)+90


4201    mapflag=0
        if lng>318.8 and lng<320.7 then lng =319.76:lat=71.37:mapflag=1

        MAPx=lng*11520/360
        MAPy=lat*5760/180
        MAPx=cint(MAPx)
        MAPy=cint(MAPy)
        MAPcornerX = MAPx-32: if MAPcornerX<1 then MAPcornerX=1
        MAPcornerY = MAPY-16: if MAPcornerY<1 then MAPcornerY=1
        MAPupcornerX=MAPcornerX+64: if MAPupcornerX>11520 then MAPcornerX=10880:MAPupcornerX=11520
        MAPupcornerY=MAPcornerY+32: if MAPupcornerY>5760 then MAPcornerY=5440:MAPupcornerY=5760
        if mapflag=1 then 4220
        
        open "R", #1, "marsLGa.bmp",1
        a$ = " " 
'1079
'for i=1 to 10000000
        'locate 1,1:print MAPcornerX, MAPcornerY, MAPupcornerX, MAPupcornerY;
        for i=MAPcornerY to MAPupcornerY
            for j=MAPcornerX to MAPupcornerX
                l=((i-1)*11520)+j+1078
                get #1, l, a$
                c=asc(a$)
                'pset (10*(j-MAPcornerX),320-(10*(i-MAPcornerY))-1),c
                line (10*(j-MAPcornerX),320-(10*(i-MAPcornerY))-1)-(10*(j-MAPcornerX)+9,320-(10*(i-MAPcornerY))-10),c,BF
            next j
        next i
        close #1
        'pset (320,160),0
        return
        
4220
        open "R", #1, "marsdst.bmp",1
        a$ = " " 
'1079
'for i=1 to 10000000
        'locate 1,1:print MAPcornerX, MAPcornerY, MAPupcornerX, MAPupcornerY;
        for i=0 to 319
            for j=0 to 639
                l=((i-1)*640)+j+1079
                get #1, l, a$
                c=asc(a$)
                pset (j,319-i),c
            next j
        next i
        close #1
        return
        
        
5000    z$="  "
        dspflag=0
        GOSUB 300
        x1 = 640 * (Ahab + 59.25 + 180) / 360
        IF x1 > 640 THEN x1 = x1 - 640
        y1 = 50 * SIN((x1 - MASRrefLAT) / 101.859164#)
        lngW = 11520*x1/640  'ABS((x1 * 57.29578 / 101.859164#))
        latW = 5760 *(y1+160)/320   '(y1 * 57.29578 / 101.859164#) + 90
        lng = int(lngW)
        lat = int(latW)
        goto 5100
        
5050    dspflag=1
        lngW = 11520*x7/640  'ABS((x1 * 57.29578 / 101.859164#))
        latW = 5760 *(y7+160)/320   '(y1 * 57.29578 / 101.859164#) + 90
        lng = int(lngW)
        lat = int(latW)


5100            j=1+(lng)+(lat*11520)
                get #5, j, z$
                h1=cvi(z$)
                'if dspflag=1 then locate 1,1:print using "###########"; j;h1;

                j=1+(lng)+((lat+1)*11520)
                get #5, j, z$
                h2=cvi(z$)
                'if dspflag=1 then locate 2,1:print using "###########"; j;h2;

                if LNG=11519 then j=1+(lat*11520)  else j=1+(lng+1)+(lat*11520)
                get #5, j, z$
                h3=cvi(z$)
                'if dspflag=1 then locate 3,1:print using "###########"; j;h3;

                if LNG=11519 then j=1+((lat+1)*11520)  else j=1+(lng+1)+((lat+1)*11520)
                get #5, j, z$
                h4=cvi(z$)
                'if dspflag=1 then locate 4,1:print using "###########"; j;h4;
                
                        LATdel=latW-lat
                        LNDdel=lngW-lng
                        h=h1*(1-LATdel)*(1-LNGdel)
                        h=h+(h2*(LATdel)*(1-LNGdel))
                        h=h+(h3*(1-LATdel)*(LNGdel))
                        h=h+(h4*(LATdel)*(LNGdel))
                'if dspflag=1 then locate 6,1:print h;
                 return
                if dspflag=0 then return
                if setflag = 0 then return
                setflag = 0
                setcount=setcount+1
                locate 2,60:print setcount;
                z$=mki$(0)
                j=1+(lng)+(lat*11520)
                put #5, j, z$
                locate 1,21:print j;
                get #5, j, z$:print cvi(z$);:z$=mki$(0)
                
                j=1+(lng)+((lat+1)*11520)
                put #5, j, z$
                locate 2,21:print j;
                get #5, j, z$:print cvi(z$);:z$=mki$(0)
                
                if LNG=11519 then j=1+(lat*11520)  else j=1+(lng+1)+(lat*11520)
                put #5, j, z$
                locate 3,21:print j;
                get #5, j, z$:print cvi(z$);:z$=mki$(0)
                
                if LNG=11519 then j=1+((lat+1)*11520)  else j=1+(lng+1)+((lat+1)*11520)
                put #5, j, z$
                locate 4,21:print j;
                get #5, j, z$:print cvi(z$);:z$=mki$(0)
                return
                

