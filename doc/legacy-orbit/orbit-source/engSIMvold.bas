        ON ERROR GOTO 2000
        DIM switch(65, 16), switchlist(255), switchlabel$(30), source(10, 5), BattAH(10), EL(15)
        DIM SOURCEs(6, 3), DEVICEs(70), SWITCHs%(70), SHORTc(10), engineOP(4), coolant(10, 4), RAD(12, 3), coolantPUMP(10), Zvar#(30)
        'Is1 to Is5:     EL(1) to EL(5)
        'Vbus1 to Vbus5: EL(6) to EL(10)
        'Ibus1 to Ibus5: EL(11) to EL(15)
        PALETTE 6, 52
        PALETTE 7, 56
        locate 1,1,0
        
        OPEN "R", #2, "OSBACKUP", 8
        inpSTR$=space$(8)
        GET #2, 1, inpSTR$
        inpFLAG$=right$(inpSTR$,7)
        outSTR$ = left$(inpSTR$,1)+"ORBIT5S"
        PUT #2, 1, outSTR$
        CLOSE #2


        z$="H"
        zpath$=""
        reload$="y"
        Zvar#(3) = 5555
        Zvar#(4) = 5555555        

1111    CLS
         
        FOR i = 1 TO 4
         LOCATE 3, 53 + (6 * i) + 1: COLOR 14, 0: PRINT CHR$(186);
         LOCATE 4, 53 + (6 * i) + 1: COLOR 14, 0: PRINT CHR$(186);
         LOCATE 5, 53 + (6 * i) + 1: COLOR 14, 0: PRINT CHR$(186);
         LOCATE 5, 50 + (6 * i) + 1: COLOR 14, 0: PRINT CHR$(186);
        NEXT i
        
        LOCATE 6, 15: COLOR 1, 2 + HP: PRINT " HAB POWER BUS: "; : PRINT USING "###########"; HPw; : PRINT " W"; SPACE$(36);
        LOCATE 14, 15: COLOR 1, 2 + AP: PRINT "AYSE POWER BUS: "; : PRINT USING "###########"; APw; : PRINT " W"; SPACE$(36);
        LOCATE 10, 25: COLOR 1, 2 + SP: PRINT "2"; CHR$(248); " BUS: "; : PRINT USING "######"; SPw; : PRINT " W         ";
        LOCATE 10, 52: COLOR 1, 2 + TP: PRINT "3"; CHR$(248); " BUS: "; : PRINT USING "####"; SPw; : PRINT " W      ";
        LOCATE 9, 56: COLOR 14, 0: PRINT CHR$(186);
        LOCATE 9, 67: PRINT CHR$(186);
        LOCATE 11, 67: PRINT CHR$(186);
        LOCATE 8, 49: PRINT CHR$(201);
        LOCATE 8, 50: PRINT CHR$(205); CHR$(17); CHR$(205);
        LOCATE 8, 53: PRINT CHR$(187);
        LOCATE 9, 53: PRINT CHR$(186);
        LOCATE 10, 76: PRINT CHR$(186);
        
        COLOR 1, 2
        LOCATE 16, 16: PRINT "AYSE   ";
        COLOR 6, 0: LOCATE 24, 64: PRINT "F12";
        
        
        
        COLOR 1, 2
        LOCATE 8, 16: PRINT "HABITAT";
        COLOR 7, 0
        LOCATE 1, 2: FOR i = 1 TO 78: PRINT CHR$(196); : NEXT i
        LOCATE 21, 2: FOR i = 1 TO 22: PRINT CHR$(196); : NEXT i
        LOCATE 17, 25: FOR i = 24 TO 78: PRINT CHR$(196); : NEXT i
        LOCATE 1, 1: PRINT CHR$(218);
        LOCATE 1, 14: PRINT CHR$(194);
        LOCATE 21, 1: PRINT CHR$(192);
        LOCATE 1, 80: PRINT CHR$(191);
        LOCATE 17, 80: PRINT CHR$(217);
        LOCATE 21, 24: PRINT CHR$(217);
        FOR i = 2 TO 20
         IF i > 16 THEN j = 24 ELSE j = 80
         LOCATE i, j: PRINT CHR$(179);
         LOCATE i, 14: PRINT CHR$(179);
         LOCATE i, 1: PRINT CHR$(179);
        NEXT i
        LOCATE 13, 1
        PRINT CHR$(195);
        FOR i = 1 TO 78: PRINT CHR$(196); : NEXT i
        PRINT CHR$(180);
        COLOR 7, 0
        LOCATE 13, 14: PRINT CHR$(197);
        LOCATE 21, 14: PRINT CHR$(193);
        LOCATE 11, 75: PRINT CHR$(218); CHR$(215); CHR$(191);
        LOCATE 12, 75: PRINT CHR$(179);
        LOCATE 12, 77: PRINT CHR$(179);
        LOCATE 13, 75: PRINT CHR$(193); CHR$(215); CHR$(193);
        LOCATE 17, 24: PRINT CHR$(218);
        LOCATE 8, 25: COLOR 1, 2 + reg1: PRINT "TRN";
        LOCATE 8, 75: COLOR 1, 2 + reg2: PRINT "TRN";
        LOCATE 6, 2: COLOR 9, 0: PRINT "FUEL";
        LOCATE 15, 2: COLOR 9, 0: PRINT "FUEL";
        LOCATE 7, 10: COLOR 9, 0: PRINT "kg";
        LOCATE 8, 10: COLOR 9, 0: PRINT "kg/h";
        LOCATE 16, 10: COLOR 9, 0: PRINT "kg";
        LOCATE 17, 10: COLOR 9, 0: PRINT "kg/h";


        COLOR 6, 0: LOCATE 23, 66: PRINT CHR$(217);
        
        COLOR 6, 0: LOCATE 24, 1: PRINT "W";
        LOCATE 18, 25: PRINT "F11"; : COLOR 9, 0: PRINT " display";
        LOCATE 19, 25: COLOR 6, 0: PRINT "TAB"; : COLOR 9, 0: PRINT " Eng clnt";
        LOCATE 20, 25: COLOR 6, 0: PRINT "PgU"; : COLOR 9, 0: PRINT " pmp sel";
        LOCATE 21, 25: COLOR 6, 0: PRINT "PgD"; : COLOR 9, 0: PRINT " pmp sel";
        LOCATE 22, 25: COLOR 6, 0: PRINT CHR$(24); CHR$(25); : COLOR 9, 0: PRINT "  rad sel";
        LOCATE 23, 25: COLOR 6, 0: PRINT "-"; : COLOR 9, 0: PRINT "  rad stow";
        LOCATE 24, 25: COLOR 6, 0: PRINT "*"; : COLOR 9, 0: PRINT "  pumps";
        LOCATE 25, 25: COLOR 6, 0: PRINT "/"; : COLOR 9, 0: PRINT "  rad loop";

       
        FOR i = 1 TO 3
         LOCATE 17 + i, 38: COLOR 9, 0: PRINT "coolant   T:    P:";
         LOCATE 17 + i, 46: COLOR 11, 0: PRINT USING "#"; i;
        NEXT i
        FOR i = 1 TO 5
         LOCATE 20 + i, 38: COLOR 9, 0: PRINT "RAD ";
         COLOR 11, 0: PRINT USING "#"; i;
         IF i < 4 THEN LOCATE 20 + i, 51: COLOR 9, 0: PRINT "RAD ";
         IF i < 4 THEN COLOR 11, 0: PRINT USING "#"; i + 5;
        NEXT i
        COLOR 14, 0
        LOCATE 11, 76: PRINT CHR$(186);
        LOCATE 13, 76: PRINT CHR$(186);



        ttUP = TIMER
        OPEN "I", #1, "obit5sej.txt"
        FOR i = 1 TO 18
         INPUT #1, x, y
         INPUT #1, switch(x, y)
        NEXT i
        FOR i = 1 TO 5
         INPUT #1, source(i, 1)
        NEXT i
        FOR i = 1 TO 3
         SHORTc(i) = 1E+25
        NEXT i

        IF z$ <> "H" THEN 8
        RCcap = 2000
        switch(0, 8) = 81
        switch(56, 8) = 81
        FOR i = 0 TO 13
         switch(i, 11) = 3
        NEXT i
        FOR i = 1 TO 6
         coolantPUMP(i) = 3
        NEXT i
        switch(38, 5) = 1
        switch(39, 5) = 1
        switch(43, 5) = 1
        switch(44, 5) = 1
        switch(40, 5) = 1
        switch(18, 5) = 1
        switch(14, 5) = 1
        switch(20, 5) = 1

        
8       EL(9) = 100000
        BattAH(1) = 10000
        BattAH(2) = 9999
        BattAH(3) = 99
        COLOR 6, 0
        FOR i = 0 TO 57
         INPUT #1, switch(i, 1)
         INPUT #1, switch(i, 2)
         INPUT #1, switch(i, 3)
         INPUT #1, switch(i, 4)
         INPUT #1, z$
         switchlist(switch(i, 1)) = i
         IF ABS(44.5 - i) < 11 THEN 18
         IF i = 57 THEN 19
         IF z$ = "" THEN LOCATE switch(i, 2), switch(i, 3): PRINT CHR$(switch(i, 1));
         IF z$ <> "" THEN LOCATE switch(i, 2), switch(i, 3) + 1 - LEN(z$): PRINT z$;
         GOTO 19
18       switchlabel$(i - 33) = z$
         IF i <> 55 THEN LOCATE switch(i, 2), switch(i, 3): PRINT CHR$(switch(i, 1));
19      NEXT i
        FOR i = 0 TO 34
         INPUT #1, k
         FOR j = 12 TO 16
          INPUT #1, switch(k, j)
         NEXT j
        NEXT i
        FOR i = 1 TO 8
         INPUT #1, RAD(i, 0)
         INPUT #1, RAD(i, 1)
         INPUT #1, RAD(i, 2)
         INPUT #1, j
         INPUT #1, switch(j, 5)
        NEXT i
        CLOSE #1
        LOCATE 25, 38: COLOR 9, 0: PRINT "RAD "; : COLOR 11, 0: PRINT "5";
        LOCATE 25, 25: COLOR 6, 0: PRINT "/"; : COLOR 9, 0: PRINT "  rad loop";

        IF reload$ = "y" THEN GOSUB 830
        tt = TIMER

1       warnFLAG = warnFLAG + .01: IF warnFLAG >= 1 THEN warnFLAG = 0
        COLOR 9, 0: LOCATE 2, 2: PRINT "HAB:  "; : COLOR 11, 0: IF Zvar#(13) = 150 THEN PRINT " OFF  ";  ELSE PRINT USING "###.#"; Zvar#(25); : COLOR 9, 0: PRINT "%";
        COLOR 9, 0: LOCATE 14, 2: PRINT "AYSE: "; : COLOR 11, 0: IF Zvar#(13) = 0 THEN PRINT " OFF  ";  ELSE PRINT USING "###.#"; Zvar#(25); : COLOR 9, 0: PRINT "%";
        
        LOCATE 7, 2: PRINT USING "########"; Zvar#(3);
        LOCATE 8, 2: PRINT USING "######.#"; HABfuelRATE#;
        
        LOCATE 16, 2: PRINT USING "########"; Zvar#(4);
        LOCATE 17, 2: PRINT USING "######.#"; AYSEfuelRATE#;
       
        LOCATE 3, 29: COLOR 6, 1: PRINT "y";
        LOCATE 3, 30: COLOR 6, 1 + switch(45, 5): PRINT " ";
        COLOR 9 - (8 * switch(45, 5)), 1 + switch(45, 5): PRINT USING "####"; AgravAcc;
        LOCATE 3, 15: COLOR 6, 1: PRINT CHR$(17); CHR$(16); " ";
        COLOR 9, 1: PRINT USING "########"; Zvar#(24); : PRINT "% "
       
        COLOR 14, 0
        FOR i = 0 TO 33
         LOCATE switch(i, 2), switch(i, 4): PRINT CHR$(206 - (switch(i, 5) * 20));
         IF switch(i, 11) = 10 THEN 5
         z$ = CHR$(switch(i, 11) + 48)
         IF switch(i, 11) = 3 THEN z$ = "B"
         IF switch(i, 11) = 16 THEN z$ = "0"
         IF switch(i, 11) = 32 THEN z$ = "3"
         IF LOADdisp < 3 THEN z$ = " "
         LOCATE switch(i, 2), switch(i, 4) + SGN(32.5 - i): PRINT z$;
         IF i = 16 THEN LOCATE 11, 53: PRINT CHR$(206 - ((1 - switch(i, 5)) * 20));
5       NEXT i
        LOCATE 7, 60: PRINT CHR$(206 - (20 * switch(50, 5)));

        LOCATE switch(56, 2), switch(56, 4): COLOR 14, 0: PRINT CHR$(206 - (switch(56, 5) * 20));
        IF switch(56, 11) = 16 THEN z$ = "0" ELSE z$ = "3"
        IF LOADdisp < 3 THEN z$ = " " 'ELSE z$ = CHR$(48 + ((switch(56, 11) - 16) / 4)
        LOCATE switch(56, 2), switch(56, 4) + 1: PRINT z$;
        
        LOCATE 9, 56: PRINT CHR$(206 - (switch(54, 5) * 20))
        LOCATE switch(57, 2), switch(57, 4): PRINT CHR$(206 - (switch(57, 5) * 20));
        LOCATE 9, 64: PRINT CHR$(206 - (switch(58, 5) * 20));
        LOCATE 9, 62: PRINT CHR$(206 - (switch(51, 5) * 20));


        FOR i = 34 TO 54
         IF i = 46 OR i = 47 THEN 3
         clr = 0
         IF i < 45 THEN 4
         IF (SWITCHs%(i) AND 3) + warnFLAG > 1.5 THEN clr = 12
4        LOCATE switch(i, 2), switch(i, 3) + 1: COLOR 9 + switch(i, 5), clr: PRINT switchlabel$(i - 33);
3       NEXT i
        i = 46: LOCATE switch(i, 2), switch(i, 3) + 1: COLOR 9 + switch(i, 5), 1: PRINT switchlabel$(i - 33);
        IF switch(0, 8) < 80 THEN clr = 9 ELSE clr = 10
        IF switch(0, 8) > 100 THEN clr = 14
        IF switch(0, 8) > 110 THEN clr = 12
        COLOR clr, 1
        PRINT USING "###"; switch(0, 8);
       
        i = 47: LOCATE switch(i, 2), switch(i, 3) + 1: COLOR 9 + switch(i, 5), 1: PRINT switchlabel$(i - 33);
        IF switch(56, 8) < 80 THEN clr = 9 ELSE clr = 10
        IF switch(56, 8) > 100 THEN clr = 14
        IF switch(56, 8) > 110 THEN clr = 12
        COLOR clr, 1
        PRINT USING "###"; switch(56, 8);
        COLOR 14, 0

        LOCATE 12, 76: IF Zvar#(13) = 150 THEN PRINT CHR$(186);  ELSE PRINT CHR$(205);
        COLOR 1 + (9 * (Zvar#(13) / 150)), 0: LOCATE 23, 68: PRINT "AYSE LTCH";
        IF Zvar#(13) = 150 THEN COLOR 8, 0 ELSE COLOR 10, 0
        IF pressure > .05 THEN clr = 10 ELSE clr = 9
        COLOR clr, 0: LOCATE 5, 4: PRINT "AIR INTAKE";
       
            
        FOR i = 1 TO 3
         IF coolant(i, 0) < 51 THEN COLOR 10, 0 ELSE COLOR 14, 0
         IF coolant(i, 0) > 80 THEN COLOR 12 * SGN(CINT(warnFLAG + .25)), 0
         LOCATE 17 + i, 50: IF LOADdisp = 1 THEN PRINT "";  ELSE PRINT USING "###"; coolant(i, 0);
         LOCATE 17 + i, 56: IF LOADdisp = 1 THEN LOCATE 17 + i, 59 ELSE PRINT USING "###"; coolant(i, 2);
         IF PUMPselect = i AND PUMPadj = 1 THEN coolantPUMP(i) = coolantPUMP(i) + 1
         IF coolantPUMP(i) > 3 THEN coolantPUMP(i) = 0
         IF (2 AND DEVICEs(i)) = 2 THEN coolantPUMP(i) = (1 AND coolantPUMP(i))
         IF (2 AND DEVICEs(3 + i)) = 2 THEN coolantPUMP(i) = (2 AND coolantPUMP(i))
         IF PUMPselect = i THEN clrb = 3 ELSE clrb = 0
         IF (1 AND DEVICEs(i)) + warnFLAG > 1.5 THEN clrb = 12
         COLOR 10 + ((12 AND DEVICEs(i)) / 2), clrb
         PRINT CHR$(45 - (2 AND coolantPUMP(i)) * 15);
         IF PUMPselect = i THEN clrb = 3 ELSE clrb = 0
         IF (1 AND DEVICEs(3 + i)) + warnFLAG > 1.5 THEN clrb = 12
         COLOR 10 + ((12 AND DEVICEs(3 + i)) / 2), clrb
         PRINT CHR$(45 - (1 AND coolantPUMP(i)) * 30);
        NEXT i
        PUMPadj = 0
        COLOR 10, 0
        IF LOADdisp = 1 THEN LOCATE 18, 50: PRINT USING "###"; SGN(coolantPUMP(1) AND 2) * EL(6) / 1000;
        IF LOADdisp = 1 THEN LOCATE 18, 56: PRINT USING "###"; SGN(coolantPUMP(1) AND 1) * EL(7) / 10;
        IF LOADdisp = 1 THEN LOCATE 19, 50: PRINT USING "###"; SGN(coolantPUMP(2) AND 2) * EL(6) / 1000;
        IF LOADdisp = 1 THEN LOCATE 19, 56: PRINT USING "###"; SGN(coolantPUMP(2) AND 1) * EL(7) / 10;
        IF LOADdisp = 1 THEN LOCATE 20, 50: PRINT USING "###"; SGN(coolantPUMP(3) AND 2) * EL(9) / 1000;
        IF LOADdisp = 1 THEN LOCATE 20, 56: PRINT USING "###"; SGN(coolantPUMP(3) AND 1) * EL(9) / 2000;

       
       
        LOCATE 12, 52: COLOR 1, 2: PRINT "BAT   "; : LOCATE 12, 58: PRINT USING "#####"; BattAH(2); : PRINT "Ah";
        LOCATE 24, 11: COLOR 6, 0: PRINT "Y "; : COLOR 9 + PARA, 12 * SGN(INT(((SWITCHs%(59) AND 3) / 2) + warnFLAG)): PRINT "CHUTE";
        LOCATE 25, 11: COLOR 6, 0: PRINT "Z";
        IF SRBused = 1 THEN COLOR 8, 0 ELSE COLOR 9, 0
        IF SRB = 1 THEN COLOR 10, 0
        PRINT " SRB";
        
       
        COLOR 1, 2
        LOCATE 9, 16
        IF LOADdisp = 1 THEN PRINT USING "##.####"; EL(6) * Hreactor / 1000;  ELSE PRINT "REACTOR";
        LOCATE 17, 16
        IF LOADdisp = 1 THEN PRINT USING "##.####"; EL(9) * Areactor / 1000;  ELSE PRINT "REACTOR";
       

        IF switch(19, 5) = 1 AND EL(6) > 8333 THEN clr = 2 ELSE clr = 6
        IF switch(19, 5) = 0 OR EL(6) < 100 THEN clr = 7
        IF (3 AND SWITCHs%(19)) + warnFLAG > 1.5 THEN clr = 12
        LOCATE 4, 51: COLOR 1, clr: PRINT "RCSP";
       

        IF switch(48, 5) + switch(49, 5) = 2 THEN switch(48, 5) = 0: switch(49, 5) = 0
        IF switch(48, 5) = 1 THEN COLOR 10, 0 ELSE COLOR 9, 0
        LOCATE 20, 68: PRINT "DETACH MOD";
        IF switch(49, 5) = 1 THEN COLOR 10, 0 ELSE COLOR 9, 0
        LOCATE 21, 68: PRINT "DOCK MOD";
        COLOR 9 + switch(50, 5), 12 * SGN(INT(((SWITCHs%(50) AND 3) / 2) + warnFLAG)): LOCATE 23, 3
        IF LOADdisp = 1 THEN PRINT USING "###_  "; switch(50, 5) * EL(6) / 100;  ELSE PRINT "RADAR";
        COLOR 9 + switch(51, 5), 12 * SGN(SWITCHs%(51)): LOCATE 22, 3
        IF LOADdisp = 1 THEN PRINT USING "###"; switch(51, 5) * EL(8) / 60;  ELSE PRINT "INS";
        COLOR 9 + switch(58, 5), 12 * SGN(INT(((SWITCHs%(58) AND 3) / 2) + warnFLAG)): LOCATE 24, 3
        IF LOADdisp = 1 THEN PRINT USING "###"; switch(58, 5) * EL(8) / 60;  ELSE PRINT "LOS";
        COLOR 9 + switch(54, 5), 12 * SGN(SWITCHs%(54)): LOCATE 25, 3
        IF LOADdisp = 1 THEN PRINT USING "###"; switch(54, 5) * EL(8) / 120;  ELSE PRINT "GNC";
        'LOCATE 1, 1: PRINT switch(52, 11);
        COLOR switch(52, 8), 12 * SGN(INT(((SWITCHs%(52) AND 3) / 2) + warnFLAG)): LOCATE 22, 13: PRINT "DEPLY PAK";
        COLOR 9 + switch(53, 5), 12 * SGN(INT(((SWITCHs%(53) AND 3) / 2) + warnFLAG)): LOCATE 23, 13: PRINT "ACTVT PAK";


        IF ABS(RADselect - 5) < 2 THEN RADstow = 0
        FOR i = 1 TO 5
         LOCATE 20 + i, 44
         fgclr = (2 * (2 ^ ((i - 1) * 3)) AND SWITCHs%(64))
         IF fgclr = 0 THEN fgclr = 14 ELSE fgclr = 12
         IF RADselect = i THEN COLOR fgclr, 3 ELSE COLOR fgclr, 0
         IF RADselect = i AND RADadj = 1 THEN RAD(i, 1) = RAD(i, 1) + 1
         IF RADselect = i AND RADstow = 1 + ((2 ^ ((i - 1) * 3)) AND SWITCHs%(64)) THEN RAD(i, 2) = 1 - RAD(i, 2)
         IF RAD(i, 1) > 2 THEN RAD(i, 1) = 0
         RAD(i, 1) = RAD(i, 1) * RAD(i, 2)
         IF RAD(i, 1) = 0 THEN z$ = "ISOL" ELSE z$ = "LP-" + CHR$(RAD(i, 1) + 48)
         IF RAD(i, 2) = 0 THEN z$ = "STWD"
         PRINT z$;
         IF i > 3 THEN 89
         LOCATE 20 + i, 57
         IF i = 1 THEN RADsel = 2 ELSE RADsel = 3
         IF RADselect = i + 5 THEN COLOR 14, 3 ELSE COLOR 14, 0
         IF RADselect = i + 5 AND RADadj = 1 THEN RAD(i + 5, 1) = RADsel - RAD(i + 5, 1)
         IF RADselect = i + 5 AND RADstow = 1 THEN RAD(i + 5, 2) = 1 - RAD(i + 5, 2)
         RAD(i + 5, 1) = RAD(i + 5, 1) * RAD(i + 5, 2)
         IF RAD(i + 5, 1) = 0 THEN z$ = "ISOL" ELSE z$ = "LP-" + CHR$(RAD(i + 5, 1) + 48)
         IF RAD(i + 5, 2) = 0 THEN z$ = "STWD"
         PRINT z$;
89      NEXT i
        IF Zvar#(13) < 150 THEN RAD(6, 1) = 0
        RADstow = 0
        RADadj = 0



        z$ = INKEY$
        'IF z$ = "W" THEN switch(58, 5) = 1 - switch(58, 5)
        'IF z$ = "/" THEN RADadj = 1: GOTO 2
        'IF z$ = "*" THEN PUMPadj = 1: GOTO 2
        'IF z$ = "-" THEN RADstow = 1: GOTO 2
        'IF z$ = "Z" AND SRBused = 0 THEN SRB = 1: SRBused = 1: SRBtimer = 0
        'IF z$ = "Y" AND SWITCHs%(59) = 0 THEN PARA = 1 - PARA
        IF z$ = CHR$(0) + CHR$(133) THEN LOADdisp = LOADdisp + 1: IF LOADdisp = 4 THEN LOADdisp = 0
        'IF z$ = CHR$(13) AND switch(55, 5) = 1 THEN Zvar#(13) = 150 - Zvar#(13)
        IF AYSEdist > 300 THEN Zvar#(13) = 0
        IF z$ = CHR$(27) THEN run "orbit5vS"
        'IF z$ = CHR$(9) THEN GOSUB 880
        IF z$ = "" THEN 2
        'IF z$ = CHR$(0) + CHR$(77) AND Zvar#(24) < 100 THEN Zvar#(24) = Zvar#(24) + 1: GOTO 2
        'IF z$ = CHR$(0) + CHR$(75) AND Zvar#(24) > 0 THEN Zvar#(24) = Zvar#(24) - 1: GOTO 2
        'IF z$ = CHR$(0) + "H" THEN RADselect = RADselect - 1: GOTO 2
        'IF z$ = CHR$(0) + "P" THEN RADselect = RADselect + 1: GOTO 2
        'IF z$ = CHR$(0) + "I" THEN PUMPselect = PUMPselect - 1: GOTO 2
        'IF z$ = CHR$(0) + "Q" THEN PUMPselect = PUMPselect + 1: GOTO 2
        'IF z$ = "z" AND LOADdisp < 3 THEN switch(0, 5) = 1 - switch(0, 5)
        'IF z$ = "z" AND LOADdisp = 3 THEN switch(0, 11) = switch(0, 11) + 1: IF switch(0, 11) = 4 THEN switch(0, 11) = 0
        'IF z$ = "u" THEN switch(65, 5) = 1 - switch(65, 5)
        'IF z$ = CHR$(0) + CHR$(133) THEN switch(54, 5) = 1 - switch(54, 5): GOTO 2
        'IF z$ = CHR$(0) + CHR$(134) THEN switch(55, 5) = 1 - switch(55, 5): GOTO 2
        'IF LEN(z$) > 1 THEN z$ = CHR$(ASC(RIGHT$(z$, 1)) - 58)
        'IF switchlist(ASC(z$)) = 0 THEN 2
        'IF LOADdisp < 3 THEN switch(switchlist(ASC(z$)), 5) = 1 - switch(switchlist(ASC(z$)), 5)': LOCATE 1, 40: PRINT switchlist(ASC(Z$));
        'IF LOADdisp = 3 AND (4096 AND SWITCHs%(switchlist(ASC(z$)))) = 4096 THEN 2
        'IF LOADdisp = 3 AND switch(switchlist(ASC(z$)), 11) < 4 THEN switch(switchlist(ASC(z$)), 11) = switch(switchlist(ASC(z$)), 11) + 1: IF switch(switchlist(ASC(z$)), 11) > 3 THEN switch(switchlist(ASC(z$)), 11) = 0
        'IF LOADdisp = 3 AND switch(switchlist(ASC(z$)), 11) > 15 THEN switch(switchlist(ASC(z$)), 11) = 48 - switch(switchlist(ASC(z$)), 11)
        

2       gosub 830
        'V = INP(889)
        'IF V AND 8 THEN switch(21, 5) = 1 ELSE switch(21, 5) = 0
        'IF V AND 32 THEN switch(23, 5) = 1 ELSE switch(23, 5) = 0
        'IF V AND 64 THEN switch(22, 5) = 1 ELSE switch(22, 5) = 0
        'IF V AND 128 THEN switch(57, 5) = 0 ELSE switch(57, 5) = 1
        'LOCATE 1, 10: IF z$ <> "" THEN PRINT switchlist(ASC(z$));

        IF Zvar#(13) = 150 THEN FOR i = 6 TO 13: switch(i, 5) = 0: NEXT i
        IF Zvar#(13) = 0 THEN FOR i = 29 TO 33: switch(i, 5) = 0: NEXT i
        COLOR 10, 0
        IF TIMER - tt < 1 THEN 1
        DELtime# = 0
        
        IF TIMER - ttUP > 10 THEN ttUP = TIMER
        IF TIMER - ttUP < 3 THEN GOSUB 810: ttUP = TIMER
        LOCATE 18, 62
        if orbTELEMflag>0 or engTELEMflag>0 then color 14
        PRINT USING "####_:"; year;
        PRINT USING "###_:"; day;
        PRINT USING "##_:"; hr;
        PRINT USING "##_:"; min;
        PRINT USING "##"; sec;
        color 8+orbTELEMflag,0: print "O";
        color 8+engTELEMflag,0: print "E";

        IF RADselect < 0 THEN RADselect = 8
        IF RADselect > 8 THEN RADselect = 0
        IF PUMPselect < 0 THEN PUMPselect = 3
        IF PUMPselect > 3 THEN PUMPselect = 0

        IF switch(52, 5) = 1 AND switch(52, 11) > 119 THEN switch(52, 8) = 10 ELSE switch(52, 8) = 9
        IF switch(52, 5) = 0 AND switch(52, 11) > 0 THEN switch(52, 11) = switch(52, 11) - 1: switch(52, 8) = 5
        IF switch(52, 5) = 1 AND switch(52, 11) < 120 THEN switch(52, 11) = switch(52, 11) + 1: switch(52, 8) = 2


        LOCATE 2, 34
        mstrALARM = 1 - mstrALARM
        IF (1 and Zvar#(26)) = 1 THEN COLOR 12 * mstrALARM, 0: PRINT "MASTER ALARM"; : beep ELSE COLOR 0, 0: PRINT "MASTER ALARM";
        COLOR 7, 0

        LOCATE 3, 51: COLOR 6, 0: PRINT "u";
        LOCATE 3, 52: COLOR 7, 1: IF switch(65, 5) = 0 THEN PRINT "PLS";  ELSE PRINT "CNT";

        GOSUB 200
        GOSUB 300
        
        IF RCcap < 1400 THEN clr = 14 ELSE clr = 10
        IF RCcap < 250 THEN clr = 12
        IF RCcap < 0 THEN RCcap = 0
        LOCATE 3, 37: COLOR clr, 1: PRINT USING "#########"; RCcap; : PRINT " As ";
        IF switch(38, 5) = 1 THEN switch(46, 5) = 0
        IF switch(39, 5) = 1 THEN switch(46, 5) = 0
        IF EL(6) > 9900 THEN clr = 10 ELSE clr = 14
        IF EL(6) < 9800 THEN clr = 4
        LOCATE 6, 15: COLOR 1, 2 + HP: PRINT "HAB POWER BUS:  "; : COLOR clr, 2 + HP: PRINT USING "###,###,###,###,###.#"; EL(11) * EL(6) / 1000; : PRINT "kW"; SPACE$(18);
        LOCATE 6, 55: COLOR clr, 2 + HP: PRINT USING "##,###,###.#"; EL(11); : PRINT "A";
        LOCATE 6, 68: COLOR clr, 2 + HP: PRINT USING "##,###,###"; EL(6); : PRINT "V";
       
        IF EL(7) > 115 THEN clr = 10 ELSE clr = 14
        IF EL(7) < 100 THEN clr = 4
        LOCATE 10, 45: COLOR clr, 2 + SP: PRINT USING "####"; EL(7); : PRINT "V";
        LOCATE 10, 40: COLOR clr, 2 + SP: PRINT USING "####"; EL(12); : PRINT "A";
        Pbus2 = EL(7) * EL(12)
        LOCATE 10, 33: COLOR clr, 2 + SP: PRINT USING "###.#"; Pbus2 / 1000; : PRINT "kW";
       
        IF EL(8) > 115 THEN clr = 10 ELSE clr = 14
        IF EL(8) < 100 THEN clr = 4
        LOCATE 10, 69: COLOR clr, 2 + TP: PRINT USING "####"; EL(8); : PRINT "V";
        LOCATE 10, 64: COLOR clr, 2 + SP: PRINT USING "####"; EL(13); : PRINT "A";
        Pbus3 = EL(8) * EL(13)
        LOCATE 10, 59: COLOR clr, 2 + SP: PRINT USING "##.#"; Pbus3 / 1000; : PRINT "kW";
       
        IF switch(43, 5) = 1 THEN switch(47, 5) = 0
        IF switch(44, 5) = 1 THEN switch(47, 5) = 0
        IF EL(9) > 99000 THEN clr = 10 ELSE clr = 14
        IF EL(9) < 98000 THEN clr = 4
        LOCATE 14, 15: COLOR 1, 2 + HP: PRINT "AYSE POWER BUS: "; : COLOR clr, 2 + HP: PRINT USING "###,###,###,###,###.#"; EL(14) * EL(9) / 1000; : PRINT "kW";
        LOCATE 14, 55: COLOR clr, 2 + HP: PRINT USING "##,###,###.#"; EL(14); : PRINT "A";
        LOCATE 14, 68: COLOR clr, 2 + HP: PRINT USING "##,###,###"; EL(9); : PRINT "V";
        
        oldHABfuelRATE# = HABfuelRATE#
        oldAYSEfuelRATE# = AYSEfuelRATE#
       
        Phab# = (EL(1) * Vr)
        LOCATE 10, 16: COLOR 1, 2 + (2 * source(1, 2))
        IF EL(1) < 1000000 THEN PRINT USING "######"; EL(1); : PRINT "A";  ELSE PRINT USING "#####"; EL(1) / 1000; : PRINT "kA";
        HABfuelRATE# = (.05# * Phab# / 50000000#) * 3600#
       
        Phabfc# = EL(2) * Vfc
        HABfuelRATE# = HABfuelRATE# + ((.002# * Phabfc# / 2000#) * 3600#)
       
        Zvar#(3) = Zvar#(3) - (((HABfuelRATE# / 2#) + (oldHABfuelRATE# / 2#)) * DELtime# / 3600#)
        Zvar#(3) = Zvar#(3) - (HABleak * DELtime#)
        oldHABfuelRATE# = HABfuelRATE#

        'hab reactor power calculation
        IF switch(0, 8) > 79.5 AND (switch(38, 5) + switch(39, 5) > 0) THEN heat = 1.7 ELSE heat = 0
        heat = heat + (8 * (Phab# / 11400000000#) * (1 + (SOURCEs(1, 2)) / 10))
        IF switch(46, 5) = 1 THEN Heater = 2.7 * ((EL(6) ^ 2) / 1000) / 500000 ELSE Heater = 0
        heat = heat + Heater
        dev = 0: GOSUB 852
        IF RND < (switch(0, 8) - 125) / 1000 THEN source(1, 2) = 1
       
       
        heat = (EL(2) * EL(2) * source(2, 1) / 2000) * (1 + (SOURCEs(2, 2)) / 10)
        dev = 14: GOSUB 852
        LOCATE 12, 25
        COLOR clrf, 2 + (2 * source(2, 2))
        IF LOADdisp > 1 THEN PRINT "TEMP"; : PRINT USING "####"; switch(14, 8); : GOTO 75
        PRINT "FC";
        IF EL(2) < 99999 THEN PRINT USING "#####"; EL(2); : PRINT "A";  ELSE PRINT USING "####"; EL(2) / 1000; : PRINT "kA";
75      IF RND < (switch(14, 8) - 110) / 1000 THEN source(2, 2) = 1

      
        heat = (EL(3) * EL(3) * source(3, 1) / 100) * (1 + (SOURCEs(3, 2)) / 10)
        dev = 18: GOSUB 852
        LOCATE 12, 34
        COLOR clrf, 2 + (2 * source(3, 2))
        PRINT "BAT";
        IF LOADdisp > 1 THEN PRINT "     TEMP"; : PRINT USING "####"; switch(18, 8); : GOTO 76
        IF EL(3) < 9999 THEN PRINT USING "####"; EL(3); : PRINT "A";  ELSE PRINT USING "###"; EL(3) / 1000; : PRINT "kA";
        PRINT USING "######"; BattAH(1); : PRINT "Ah";
76      IF RND < (switch(18, 8) - 110) / 1000 THEN source(3, 2) = 1


        heat = (EL(4) * EL(4) * source(4, 1) / 100) * (1 + (SOURCEs(4, 2)) / 10)
        dev = 26: GOSUB 852
        LOCATE 16, 25
        COLOR clrf, 2 + (2 * source(4, 2))
        PRINT "BAT";
        IF LOADdisp > 1 THEN 77
        IF EL(4) < 9999 THEN PRINT USING "####"; EL(4); : PRINT "A";  ELSE PRINT USING "###"; EL(4) / 1000; : PRINT "kA";
        PRINT USING "###"; BattAH(3); : PRINT "Ah";
77      IF LOADdisp = 2 THEN PRINT "  TEMP"; : PRINT USING "####"; switch(26, 8);
        IF RND < (switch(26, 8) - 110) / 1000 THEN source(4, 2) = 1
       
        Payse# = (EL(5) * VrA)
        LOCATE 18, 16: COLOR 1, 2 + (2 * source(5, 2))
        IF EL(5) < 999999 THEN PRINT USING "######"; EL(5); : PRINT "A";  ELSE PRINT USING "#####"; EL(5) / 1000; : PRINT "kA";
        AYSEfuelRATE# = (.175# * Payse# / 960000000#) * 3600

        Zvar#(4) = Zvar#(4) - (((AYSEfuelRATE# / 2) + (oldAYSEfuelRATE# / 2)) * DELtime# / 3600#)
        Zvar#(4) = Zvar#(4) - (AYSEleak * DELtime#)
        oldAYSEfuelRATE# = AYSEfuelRATE#

        IF switch(56, 8) > 79.5 AND (switch(43, 5) + switch(44, 5) > 0) THEN heat = .84 ELSE heat = 0
        heat = heat + ((Payse# / 151158200000#) * (1 + (SOURCEs(5, 2)) / 10))
        IF switch(47, 5) = 1 THEN Heater = 5 * ((EL(9) ^ 2) / 100000) / 500000 ELSE Heater = 0
        heat = heat + Heater
        dev = 56: GOSUB 852
        IF RND < (switch(56, 8) - 110) / 1000 THEN source(5, 2) = 1

        IF switch(56, 8) < 30 THEN Areactor = 0
        IF AreactorRC = 2 THEN AreactorD = AreactorD + 1.1
        IF AreactorD > 0 AND EL(9) > 100 THEN AreactorD = AreactorD - .1
        IF AreactprRC = 0 AND AreactorD > 59.5 THEN AreactorD = 59.5
        IF AreactorD > 59.99 THEN source(5, 2) = 1
        LOCATE 20, 16
        clr = 0: bk = 0
        IF AreactorD > 0 THEN clr = 4: bk = 1
        IF AreactorRC = 2 THEN clr = 12: bk = 1
        IF source(5, 2) = 1 THEN clr = 0: bk = 0: AreactorD = 60
        COLOR clr, bk
        PRINT USING "#######"; 60 - AreactorD;

        
        IF Zvar#(13) = 150 AND switch(37, 5) = 1 AND Zvar#(4) > 100 THEN Zvar#(3) = Zvar#(3) + 1000: Zvar#(4) = Zvar#(4) - 1000
        IF Zvar#(13) = 0 AND switch(37, 5) = 1 AND OCESSdist < 500 THEN Zvar#(3) = Zvar#(3) + 1000
        IF Zvar#(13) = 150 AND switch(36, 5) = 1 THEN Zvar#(3) = Zvar#(3) - 1000: Zvar#(4) = Zvar#(4) + 1000
        IF Zvar#(13) = 0 AND switch(36, 5) = 1 THEN Zvar#(3) = Zvar#(3) - 1000
        IF switch(41, 5) = 1 THEN Zvar#(4) = Zvar#(4) - 1000
        IF switch(42, 5) = 1 THEN Zvar#(4) = Zvar#(4) + (1000 * pressure)
        IF Zvar#(4) < 0 THEN switch(41, 5) = 0: Zvar#(4) = 0
        IF Zvar#(3) < 0 THEN switch(36, 5) = 0: Zvar#(3) = 0
        IF Zvar#(4) > 20000000 THEN switch(42, 5) = 0: Zvar#(4) = 20000000
        IF Zvar#(3) > 200000 THEN switch(37, 5) = 0: Zvar#(3) = 200000


        habENG = 1
        FOR i = 1 TO 4
         IF switch(5 + (2 * i), 5) = 1 AND EL(6) > 8333 THEN clr = 2 ELSE clr = 6
         IF switch(5 + (2 * i), 5) = 0 OR EL(6) < 100 THEN clr = 7
         IF switch(5 + (2 * i), 6) > 0 THEN current = EL(6) / switch(5 + (2 * i), 6) ELSE current = 0
         power = EL(6) * current: dev = 5 + (2 * i): GOSUB 850
         IF (SWITCHs%(5 + (2 * i)) AND 3) + warnFLAG > 1.5 THEN clr = 12
         Zuse$ = "####"
         IF current < 100000 THEN Zuse$ = "##.#"
         IF current < 10000 THEN Zuse$ = "#.##"
         LOCATE 2, 51 + (6 * i)
         COLOR clrf, clr
         IF LOADdisp = 0 THEN PRINT "ION"; : PRINT USING "#"; i;  ELSE
         IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
         IF LOADdisp > 1 THEN PRINT USING "####"; switch(5 + (2 * i), 8);
         IF switch(4 + (2 * i), 5) = 1 AND EL(6) > 8333 THEN clr = 2 ELSE clr = 6
         IF switch(4 + (2 * i), 5) = 0 OR EL(6) < 100 THEN clr = 7
         IF switch(4 + (2 * i), 6) > 0 THEN current = EL(6) / switch(4 + (2 * i), 6) ELSE current = 0
         power = EL(6) * current: dev = 4 + (2 * i): GOSUB 850
         IF (SWITCHs%(4 + (2 * i)) AND 3) + warnFLAG > 1.5 THEN clr = 12
         Zuse$ = "####"
         IF current < 100000 THEN Zuse$ = "##.#"
         IF current < 10000 THEN Zuse$ = "#.##"
         LOCATE 4, 50 + (6 * i)
         COLOR clrf, clr
         IF LOADdisp = 0 THEN PRINT "ACC"; : PRINT USING "#"; i;
         IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
         IF LOADdisp > 1 THEN PRINT USING "####"; switch(4 + (2 * i), 8);
        NEXT i
        habENG = 0
       
        IF switch(3, 5) = 1 AND EL(6) > 8333 THEN clr = 2 ELSE clr = 6
        IF switch(3, 5) = 0 OR EL(6) < 100 THEN clr = 7
        IF switch(3, 6) > 0 THEN current = EL(6) / switch(3, 6) ELSE current = 0
        power = EL(6) * current: dev = 3: GOSUB 850
        IF (SWITCHs%(3) AND 3) + warnFLAG > 1.5 THEN clr = 12
        Zuse$ = "######"
        IF current < 100000 THEN Zuse$ = "##.###"
        IF current < 10000 THEN Zuse$ = "#.####"
        LOCATE 4, 29: COLOR clrf, clr
        IF LOADdisp = 0 THEN PRINT "A GRAV";
        IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
        IF LOADdisp > 1 THEN PRINT USING "######"; switch(3, 8);

        clr = 2
        IF RCcap <= 0 THEN clr = 7: RCcap = 0
        IF RCcap <= 0 AND switch(0, 8) >= 30 THEN source(1, 2) = 1
        IF switch(0, 8) < 30 THEN clr = 7
        IF switch(4, 6) > 0 THEN current = EL(6) / switch(4, 6) ELSE current = 0
        IF (SWITCHs%(4) AND 3) + warnFLAG > 1.5 THEN clr = 12
        power = EL(6) * current: dev = 4: GOSUB 850
        LOCATE 4, 37: COLOR 1, clr
        IF LOADdisp = 0 THEN PRINT "R-CON1";
        IF LOADdisp = 1 THEN PRINT USING "#.####"; current / 1000;
        IF LOADdisp > 1 THEN PRINT USING "######"; switch(4, 8);

        clr = 2
        IF RCcap <= 0 THEN clr = 7
        IF switch(5, 6) > 0 THEN current = EL(6) / switch(5, 6) ELSE current = 0
        IF switch(0, 8) < 30 THEN clr = 7
        power = EL(6) * current: dev = 5: GOSUB 850
        IF (SWITCHs%(5) AND 3) + warnFLAG > 1.5 THEN clr = 12
        LOCATE 4, 44: COLOR 1, clr
        IF LOADdisp = 0 THEN PRINT "R-CON2";
        IF LOADdisp = 1 THEN PRINT USING "#.####"; current / 1000;
        IF LOADdisp > 1 THEN PRINT USING "######"; switch(5, 8);


        FOR i = 1 TO 2
         IF switch(i, 5) = 1 AND EL(6) > 8333 THEN clr = 2 ELSE clr = 6
         IF switch(i, 5) = 0 OR EL(6) < 100 THEN clr = 7
         IF switch(i, 6) > 0 THEN current = EL(6) / switch(i, 6) ELSE current = 0
         power = EL(6) * current: dev = i: GOSUB 850
         IF (SWITCHs%(i) AND 3) + warnFLAG > 1.5 THEN clr = 12
         Zuse$ = "###.##"
         IF current < 100000 THEN Zuse$ = "##.###"
         IF current < 10000 THEN Zuse$ = "#.####"
         LOCATE 4, 8 + (i * 7): COLOR clrf, clr
         IF LOADdisp = 0 THEN PRINT "RAD-S"; : PRINT USING "#"; i;
         IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
         IF LOADdisp > 1 THEN PRINT USING "######"; switch(i, 8);
        NEXT i

        IF switch(20, 5) = 1 AND EL(7) > 100 THEN clr = 2 ELSE clr = 6
        IF switch(20, 5) = 0 OR EL(7) < 10 THEN clr = 7
        IF (SWITCHs%(20) AND 3) + warnFLAG > 1.5 THEN clr = 12
        IF switch(20, 5) > 0 THEN current = EL(7) * ((1 / Rcom) + (1 / 8)) ELSE current = 0
        LOCATE 8, 29: COLOR 1, clr
        IF current > 999 THEN Zuse$ = "#.#": factor = 1000 ELSE Zuse$ = "###": factor = 1
        IF LOADdisp = 0 THEN PRINT "COM";
        IF LOADdisp = 1 THEN PRINT USING Zuse$; current / factor;
        IF LOADdisp > 1 THEN PRINT USING "###"; switch(20, 8);
      
        FOR i = 1 TO 4
         IF i < 4 THEN j = i + 20 ELSE j = 57
         IF switch(j, 5) = 1 AND EL(7) > 100 THEN clr = 2 ELSE clr = 6
         IF switch(j, 5) = 0 OR EL(7) < 10 THEN clr = 7
         IF (SWITCHs%(j) AND 3) + warnFLAG > 1.5 THEN clr = 12
         LOCATE 8, 29 + (i * 4): COLOR 1, clr: PRINT "ln"; : PRINT USING "#"; i;
        NEXT i

      
        IF EL(8) < 10 THEN clr = 7 ELSE clr = 2
        LOCATE 8, 55: COLOR 1, clr: PRINT "GNC: R I L";
        IF EL(8) < 10 THEN clr = 7 ELSE clr = 2
        LOCATE 8, 66: COLOR 1, clr: PRINT "Network";
        LOCATE 12, 66: COLOR 1, clr: PRINT "Life Sup";
      
        FOR i = 1 TO 4
         IF switch(28 + i, 5) = 1 AND EL(9) > 8333 THEN clr = 2 ELSE clr = 6
         IF switch(28 + i, 5) = 0 OR EL(9) < 100 THEN clr = 7
         IF (SWITCHs%(28 + i) AND 3) + warnFLAG > 1.5 THEN clr = 12
         IF switch(28 + i, 6) > 0 THEN current = EL(9) / switch(28 + i, 6) ELSE current = 0
         power = current * EL(9): dev = i + 28: GOSUB 850
         Zuse$ = "####"
         IF current < 100000 THEN Zuse$ = "##.#"
         IF current < 10000 THEN Zuse$ = "#.##"
         LOCATE 16, 50 + (5 * i): COLOR clrf, clr:
         IF LOADdisp = 0 THEN PRINT "GPD"; : PRINT USING "#"; i;
         IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
         IF LOADdisp > 1 THEN PRINT USING "####"; switch(28 + i, 8);
        NEXT i
        IF switch(33, 5) = 1 AND EL(9) > 8333 THEN clr = 2 ELSE clr = 6
        IF switch(33, 5) = 0 OR EL(9) < 100 THEN clr = 7
        IF (SWITCHs%(33) AND 3) + warnFLAG > 1.5 THEN clr = 12
        IF switch(33, 6) > 0 THEN current = EL(9) / switch(33, 6) ELSE current = 0
        power = current * EL(9): dev = 33: GOSUB 850
        Zuse$ = "####"
        IF current < 100000 THEN Zuse$ = "##.#"
        IF current < 10000 THEN Zuse$ = "#.##"
        LOCATE 16, 75: COLOR clrf, clr:
        IF LOADdisp = 0 THEN PRINT "TTC ";
        IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
        IF LOADdisp > 1 THEN PRINT USING "####"; switch(33, 8);
       
        AreactorRC = 0
        FOR i = 1 TO 2
         IF switch(26 + i, 5) = 1 AND EL(9) > 8333 THEN clr = 2 ELSE clr = 6
         IF switch(56, 8) < 30 THEN clr = 7
         IF (SWITCHs%(26 + i) AND 3) + warnFLAG > 1.5 THEN clr = 12
         IF switch(26 + i, 5) = 0 OR EL(9) < 100 THEN clr = 7: AreactorRC = AreactorRC + 1
         IF switch(26 + i, 6) > 0 THEN current = EL(9) / switch(26 + i, 6) ELSE current = 0
         Zuse$ = "######"
         IF current < 100000 THEN Zuse$ = "##.###"
         IF current < 10000 THEN Zuse$ = "#.####"
         LOCATE 16, 33 + (7 * i): COLOR 1, clr:
         IF LOADdisp = 0 THEN PRINT "R-CON"; : PRINT USING "#"; i;
         IF LOADdisp = 1 THEN PRINT USING Zuse$; current / 1000;
         IF LOADdisp > 1 THEN PRINT USING "######"; switch(26 + i, 8);
        NEXT i

        IF switch(56, 8) < 30 THEN AreactorRC = 0
        IF AYSEdist < 300 THEN COLOR 10, 0 ELSE COLOR 9, 0
        LOCATE 25, 68: PRINT "IN POSITION";
        IF switch(55, 5) = 1 THEN COLOR 10, 0 ELSE COLOR 9, 0
        LOCATE 24, 68: PRINT "AYSE LTCH ARM";



        'GOSUB 820
        IF SRB = 1 THEN SRBtimer = SRBtimer + DELtime#
        IF SRBtimer > 120 THEN SRB = 0
        FOR i = 1 TO 3
         coolant(i, 2) = ((1 AND coolantPUMP(i)) * 33.333) * (1 - (2 AND DEVICEs(i)) / 2)
         coolant(i, 2) = coolant(i, 2) + (((2 AND coolantPUMP(i)) * 33.333) * (1 - (2 AND DEVICEs(i + 3)) / 2))
         coolant(i, 2) = coolant(i, 2) * (1 - coolant(i, 3))
         coolant(i, 4) = (DEVICEs(6 + i) / 1500) + ((1 AND coolantPUMP(i)) * (240 AND DEVICEs(i)) / 24000) + ((2 AND coolantPUMP(i)) * (240 AND DEVICEs(i + 3)) / 48000)
        NEXT i
        FOR i = 1 TO 13
         IF (1 AND switch(i, 11)) = 1 THEN coolant(1, 4) = coolant(1, 4) + ((15 AND DEVICEs(i + 9)) / 15000)
         IF (2 AND switch(i, 11)) = 2 THEN coolant(2, 4) = coolant(2, 4) + ((240 AND DEVICEs(i + 9)) / 24000)
         IF switch(i + 20, 11) = 32 THEN coolant(3, 4) = coolant(3, 4) + ((15 AND DEVICEs(i + 29)) / 15000)
        NEXT i
        FOR i = 1 TO 3
         coolant(i, 3) = coolant(i, 3) + (coolant(i, 4) * SGN(coolant(i, 2)))
         IF coolant(i, 3) > 1 THEN coolant(i, 3) = 1
        NEXT i
        'coolant(3, 3) = 0
        'FOR i = 1 TO 15
        ' IF i < 15 THEN j = i ELSE j = 18
        ' IF (1 AND switch(j, 11)) = 1 THEN coolant(1, 2) = coolant(1, 2) * (1 - DEVICEs(21 + i))
        ' IF (2 AND switch(j, 11)) = 2 THEN coolant(1, 2) = coolant(1, 2) * (1 - DEVICEs(36 + i))
        'NEXT i

        COLOR 14, 0
        tt = TIMER
        GOSUB 860

        GOTO 1
        END


100     'Main HAB bus Resistors
        switch(4, 6) = 0
        switch(5, 6) = 0
        IF Zvar#(24) > 0 THEN switch(1, 6) = switch(1, 5) / (73.86 * Zvar#(24) / 100#) ELSE switch(1, 6) = 0
        IF Zvar#(24) > 0 THEN switch(2, 6) = switch(2, 5) / (73.86 * Zvar#(24) / 100#) ELSE switch(2, 6) = 0
        switch(3, 6) = 0
        AgravAcc = ABS(Accel# - 10) - (50 * switch(45, 5))
        IF AgravAcc < 0 THEN AgravAcc = 0
        IF AgravAcc > 1 THEN switch(3, 6) = switch(3, 5) * (1 / ((1 / 50) + (AgravAcc / 4.4)))
        FOR i = 7 TO 13 STEP 2
         switch(i, 6) = 0
         IF Zvar#(25) > 0 THEN switch(i, 6) = switch(i, 5) / (.61 * Zvar#(25) / 100#)
        NEXT i
        FOR i = 6 TO 12 STEP 2
         switch(i, 6) = 0
         IF Zvar#(25) > 0 THEN switch(i, 6) = switch(i, 5) / (11.5775 * Zvar#(25) / 100#)
        NEXT i
       
        Rt = 1 / SHORTc(1)
        FOR i = 1 TO 13
         factor = 1 + ((12 AND SWITCHs%(i)) / 120) - ((48 AND SWITCHs%(i)) / 480)
         switch(i, 6) = switch(i, 6) * factor
         IF switch(i, 6) > 0 THEN Rt = Rt + (1 / switch(i, 6))
        NEXT i
        IF switch(46, 5) = 1 THEN Rt = Rt + (1 / 1000)
        IF switch(19, 5) = 1 THEN Rt = Rt + (1 / 100000)
        'IF recharging > 0 THEN Rt = Rt + (1 / recharging)
        factor = 1 + ((12 AND SWITCHs%(50)) / 120) - ((48 AND SWITCHs%(50)) / 480)
        IF switch(50, 5) = 1 THEN Rt = Rt + (1 / (100 * factor))
        IF (coolantPUMP(1) AND 2) = 2 THEN Rt = Rt + (1 / 1000)
        IF (coolantPUMP(2) AND 2) = 2 THEN Rt = Rt + (1 / 1000)
        RCflag = 0
        IF switch(4, 5) + switch(5, 5) > 0 AND RCcap < 2000 THEN RCflag = 1: Rt = Rt + (1 / 1000)
       
109     Hreactor = 0
        IF switch(38, 5) = 1 THEN Hreactor = Hreactor + .00003
        IF switch(39, 5) = 1 THEN Hreactor = Hreactor + .00003
        IF switch(0, 8) > 30 THEN Hreactor = Hreactor + .0004
        IF switch(0, 8) > 80 THEN Hreactor = Hreactor + .00004
        Rt = Rt + (switch(0, 5) * Hreactor)
        Tsw = switch(4, 5) + switch(5, 5)
        boost = 0
        res = Rt + (switch(0, 5) * link * (1 / (Rt4 / 100)))
        IF 1 / res < .017 THEN boost = (.00000003# * res / .17)
        IF switch(4, 5) = 1 THEN switch(4, 6) = (1 / ((res) * (.001016 + boost))) * Tsw ELSE switch(4, 6) = 1E+15
        IF switch(5, 5) = 1 THEN switch(5, 6) = (1 / ((res) * (.001016 + boost))) * Tsw ELSE switch(5, 6) = 1E+15
        IF switch(4, 6) < 1E+14 AND switch(4, 6) > 10000 THEN switch(4, 6) = 10000
        IF switch(5, 6) < 1E+14 AND switch(5, 6) > 10000 THEN switch(5, 6) = 10000
        IF switch(4, 5) > 0 THEN Rt = Rt + (1 / switch(4, 6))
        IF switch(5, 5) > 0 THEN Rt = Rt + (1 / switch(5, 6))

        FOR i = 1 TO 13
         sht = (3072 AND SWITCHs%(i)) / 600
         IF sht = 0 THEN 107
         IF switch(i, 5) = 1 THEN Rt = Rt + (1 / (10 ^ (6 - sht)))
107     NEXT i
        sht = (3072 AND SWITCHs%(50)) / 600
        IF sht = 0 THEN 106
        IF switch(50, 5) = 1 THEN Rt = Rt + (1 / (10 ^ (6 - sht)))
106     Rt = 1 / Rt
        RETURN

        'HAB BUS 2 resistors
110     Rt1 = 1 / SHORTc(2)
        Rcom = (1E+12 / (OCESSdist + 1))
        IF Rcom < .2 THEN Rcom = .2
        factor = 1 + ((12 AND SWITCHs%(20)) / 120) - ((48 AND SWITCHs%(20)) / 480)
        IF switch(20, 5) = 1 THEN Rt1 = Rt1 + (1 / (Rcom * factor)) + (1 / (8 * factor))
        IF switch(21, 5) = 1 THEN Rt1 = Rt1 + (1 / 8)
        IF switch(22, 5) = 1 THEN Rt1 = Rt1 + (1 / 8)
        IF switch(23, 5) = 1 THEN Rt1 = Rt1 + (1 / 8)
        IF (coolantPUMP(1) AND 1) = 1 THEN Rt1 = Rt1 + (1 / 10)
        IF (coolantPUMP(2) AND 1) = 1 THEN Rt1 = Rt1 + (1 / 10)
        IF switch(18, 5) = 0 AND BattAH(1) < 10000 THEN Rt1 = Rt1 + (1 / 2500)
        sht = (3072 AND SWITCHs%(20)) / 600
        IF sht = 0 THEN 116
        IF switch(52, 5) = 1 THEN Rt = Rt + (1 / (10 ^ (6 - sht)))
116     Rt1 = 1 / Rt1
        RETURN
     
        'HAB BUS 3 resistors
120     Rt2 = 1 / 8
        IF switch(51, 5) = 1 THEN Rt2 = Rt2 + (1 / 60)
        IF switch(58, 5) = 1 THEN Rt2 = Rt2 + (1 / 60)
        IF switch(54, 5) = 1 THEN Rt2 = Rt2 + (1 / 120)
        IF switch(16, 5) = 1 AND BattAH(2) < 9999 THEN Rt2 = Rt2 + (1 / 2500)
        Rt2 = 1 / Rt2
        RETURN


        'AYSE BUS resistors
130     Rt4 = 1 / SHORTc(4)
        switch(33, 6) = 0
        IF Zvar#(25) > 0 THEN switch(33, 6) = switch(33, 5) / (16 * Zvar#(25) / 1850)
        IF switch(33, 5) = 0 THEN TTCeff = 100 ELSE TTCeff = 1
        FOR i = 29 TO 32
         switch(i, 6) = 0
         IF Zvar#(25) > 0 THEN switch(i, 6) = switch(i, 5) / ((40.5 / TTCeff) * Zvar#(25) / 1850)
        NEXT i
        FOR i = 29 TO 33
         factor = 1 + ((12 AND SWITCHs%(i)) / 120) - ((48 AND SWITCHs%(i)) / 480)
         IF switch(i, 6) > 0 THEN Rt4 = Rt4 + (1 / (switch(i, 6) * factor))
        NEXT i
        IF switch(56, 8) > 0 AND EL(9) < 1000 THEN switch(26, 5) = 1: switch(43, 5) = 0: switch(44, 5) = 0
        IF switch(26, 5) = 0 AND BattAH(3) < 10 THEN Rt4 = Rt4 + (1 / 2500000)
        IF switch(47, 5) = 1 THEN Rt4 = Rt4 + (1 / 100000)

139     Areactor = 0
        IF switch(43, 5) = 1 THEN Areactor = Areactor + .00003
        IF switch(44, 5) = 1 THEN Areactor = Areactor + .00003
        IF switch(56, 8) > 30 THEN Areactor = Areactor + .00002
        IF switch(56, 8) > 80 THEN Areactor = Areactor + .000005
        Rt4 = Rt4 + Areactor
        Tsw = switch(27, 5) + switch(28, 5)
        boost = 0
        IF 1 / Rt4 < .017 THEN boost = (.00000003# * Rt4 / .17)
        IF switch(27, 5) = 1 THEN switch(27, 6) = (1 / ((Rt4) * (.001016 + boost))) * Tsw ELSE switch(27, 6) = 1E+25
        IF switch(28, 5) = 1 THEN switch(28, 6) = (1 / ((Rt4) * (.001016 + boost))) * Tsw ELSE switch(28, 6) = 1E+25
        IF switch(27, 6) < 1E+24 AND switch(27, 6) > 1000000 THEN switch(27, 6) = 1000000
        IF switch(28, 6) < 1E+24 AND switch(28, 6) > 1000000 THEN switch(28, 6) = 1000000
        IF switch(27, 5) > 0 THEN Rt4 = Rt4 + (1 / switch(27, 6))
        IF switch(28, 5) > 0 THEN Rt4 = Rt4 + (1 / switch(28, 6))
        Rt4 = 1 / Rt4
        RETURN


        'Source Power Capacities
200     Hreactor = 0
        Vr = 0
        Vfc = 0
        Vb1 = 0
        Vb2 = 0
        Vb3 = 0
        VrA = 0
        GOSUB 800
        FOR i = 1 TO 59
         IF (2 AND SWITCHs%(i)) = 2 THEN switch(i, 5) = 0
        NEXT i

        IF Zvar#(3) <= 0 THEN 201
        IF switch(0, 5) = 0 THEN 203
        IF switch(0, 8) > 80 AND switch(38, 5) = 1 THEN Vr = 10000 + SOURCEs(1, 1)
        IF switch(0, 8) > 80 AND switch(39, 5) = 1 THEN Vr = 10000 + SOURCEs(1, 1)
203     IF switch(40, 5) * switch(14, 5) = 1 THEN Vfc = 120 + SOURCEs(2, 1)
201     IF BattAH(1) > 0 AND switch(18, 5) = 1 THEN Vb1 = 120 + SOURCEs(3, 1)
        IF BattAH(2) > 0 AND switch(16, 5) = 0 THEN Vb2 = 120 + SOURCEs(6, 1)
        IF BattAH(3) > 0 AND switch(26, 5) = 1 THEN Vb3 = 100000 + SOURCEs(4, 1)
        IF Zvar#(4) <= 0 THEN 204
        IF switch(56, 5) = 0 THEN 204
        IF switch(56, 8) > 80 AND switch(43, 5) = 1 THEN VrA = 100000 + SOURCEs(5, 1)
        IF switch(56, 8) > 80 AND switch(44, 5) = 1 THEN VrA = 100000 + SOURCEs(5, 1)
      


204     IF source(1, 2) = 1 THEN Vr = 0
        IF source(2, 2) = 1 THEN Vfc = 0
        IF source(3, 2) = 1 THEN Vb1 = 0
        IF source(4, 2) = 1 THEN Vb3 = 0
        IF source(5, 2) = 1 THEN VrA = 0
        link = switch(24, 5) * switch(25, 5) * (Zvar#(13) / 150)
        GOSUB 130
        GOSUB 100
        GOSUB 110
        GOSUB 120
        Vbus1max = 0
        Vbus2max = 0
        Vbus3max = 0
        Vbus4max = 0
        source(1, 1) = .00025 * (1 + SOURCEs(1, 2))
        source(2, 1) = .00325 * (1 + SOURCEs(2, 2))
        source(5, 1) = .00003 * (1 + SOURCEs(5, 2))
        source(3, 1) = .01 * (1 + (switch(18, 8) / 100) ^ 2) * (1 + SOURCEs(3, 2))
        source(4, 1) = .0055 * (1 + (switch(26, 8) / 100) ^ 2) * (1 + SOURCEs(4, 2))
        'LOCATE 25, 25
        'PRINT USING "##.####^^^^"; Rt; : PRINT " ";
        'PRINT USING "##.####^^^^"; Rt1; : PRINT " ";
        'PRINT USING "##.####^^^^"; Rt2; : PRINT " ";
        'PRINT USING "##.####^^^^"; Rt4; : PRINT " ";

        '*******************************************
        'Hab Reactor Output
        'BUS1
        V1# = Vr
        V2# = (switch(15, 5) * switch(17, 5)) * Vfc * 83.33334
        V3# = (switch(15, 5) * switch(17, 5)) * Vb1 * 83.33334
        IF V1# = 0 THEN R1# = 100000 ELSE R1# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))
        R2# = source(2, 1) * 6944.445
        R3# = source(3, 1) * 6944.445
        V4# = Vb3 * link / 10
        V5# = VrA * link / 10
        R4# = source(4, 1) / 100
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 100
        R6# = Rt
        GOSUB 900
        Ibus1R = I1#
        IF Vbus1max < V1# THEN Vbus1max = V1#
        IF Vbus1max < V2# THEN Vbus1max = V2#
        IF Vbus1max < V3# THEN Vbus1max = V3#
        IF Vbus1max < V4# THEN Vbus1max = V4#
        IF Vbus1max < V5# THEN Vbus1max = V5#

       
        'BUS2
        V1# = Vr * (switch(15, 5) * switch(17, 5))
        V2# = Vfc * 83.33334
        V3# = Vb1 * 83.33334
        IF V1# = 0 THEN R1# = 0 ELSE R1# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))
        R2# = source(2, 1) * 6944.445
        R3# = source(3, 1) * 6944.445
        V4# = Vb3 * (switch(15, 5) * switch(17, 5)) * link / 10
        V5# = VrA * (switch(15, 5) * switch(17, 5)) * link / 10
        R4# = source(4, 1) / 100
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 100
        R6# = Rt1 * 6944.445
        GOSUB 900
        Ibus2R = I1#
        

        'BUS3
        V1# = Vr * switch(15, 5) * switch(17, 5) * switch(16, 5)
        V2# = Vfc * switch(16, 5) * 83.33334
        V3# = Vb1 * switch(16, 5) * 83.33334
        IF V1# = 0 THEN R1# = 0 ELSE R1# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))
        R2# = source(2, 1) * 6944.445
        R3# = source(3, 1) * 6944.445
        V4# = Vb3 * switch(15, 5) * switch(17, 5) * switch(16, 5) * link / 10
        V5# = VrA * switch(15, 5) * switch(17, 5) * switch(16, 5) * link / 10
        R4# = source(4, 1) / 100
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 100
        R6# = Rt2 * 6944.445
        GOSUB 900
        Ibus3R = I1#


        'BUS4
        V1# = Vr * link
        V2# = Vfc * 83.33334 * link * (switch(15, 5) * switch(17, 5))
        V3# = Vb1 * 83.33334 * link * (switch(15, 5) * switch(17, 5))
        IF V1# = 0 THEN R1# = 0 ELSE R1# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))
        R2# = source(2, 1) * 6944.445
        R3# = source(3, 1) * 6944.445
        V4# = Vb3 / 10
        V5# = VrA / 10
        R4# = source(4, 1) / 100
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 100
        R6# = Rt4 / 100
        GOSUB 900
        Ibus4R = I1#
        IF Vbus4max < V1# * 10 THEN Vbus4max = V1# * 10
        IF Vbus4max < V2# * 10 THEN Vbus4max = V2# * 10
        IF Vbus4max < V3# * 10 THEN Vbus4max = V3# * 10
        IF Vbus4max < V4# * 10 THEN Vbus4max = V4# * 10
        IF Vbus4max < V5# * 10 THEN Vbus4max = V5# * 10
        '*******************************************

        '*******************************************      
        'Fuel Cell Output
        'BUS1
        V2# = Vr / 83.33334
        V1# = (switch(15, 5) * switch(17, 5)) * Vfc
        V3# = (switch(15, 5) * switch(17, 5)) * Vb1
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R1# = source(2, 1)
        R3# = source(3, 1)
        V4# = Vb3 * link / 833.3334
        V5# = VrA * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt / 6944.445
        GOSUB 900
        Ibus1fc = I1#

        'BUS2
        V2# = Vr * (switch(15, 5) * switch(17, 5)) / 83.33334
        V1# = Vfc
        V3# = Vb1
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R1# = source(2, 1)
        R3# = source(3, 1)
        V4# = Vb3 * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        V5# = VrA * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt1
        GOSUB 900
        Ibus2fc = I1#
        IF Vbus2max < V1# THEN Vbus2max = V1#
        IF Vbus2max < V2# THEN Vbus2max = V2#
        IF Vbus2max < V3# THEN Vbus2max = V3#
        IF Vbus2max < V4# THEN Vbus2max = V4#
        IF Vbus2max < V5# THEN Vbus2max = V5#

        'BUS3
        V2# = Vr * (switch(15, 5) * switch(17, 5) * switch(16, 5)) / 83.33334
        V1# = Vfc * switch(16, 5)
        V3# = Vb1 * switch(16, 5)
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R1# = source(2, 1)
        R3# = source(3, 1)
        V4# = Vb3 * switch(16, 5) * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        V5# = VrA * switch(16, 5) * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt2
        GOSUB 900
        Ibus3fc = I1#
        IF Vbus3max < V1# THEN Vbus3max = V1#
        IF Vbus3max < V2# THEN Vbus3max = V2#
        IF Vbus3max < V3# THEN Vbus3max = V3#
        IF Vbus3max < V4# THEN Vbus3max = V4#
        IF Vbus3max < V5# THEN Vbus3max = V5#

        'BUS4
        V2# = Vr * link / 83.33334
        V1# = Vfc * (switch(15, 5) * switch(17, 5)) * link
        V3# = Vb1 * (switch(15, 5) * switch(17, 5)) * link
        IF V2# = 0 THEN R2# = 0 ELSE R2# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) / 6944.445
        R1# = source(2, 1)
        R3# = source(3, 1)
        V4# = Vb3 / 833.3334
        V5# = VrA / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt4 / 694444.5
        GOSUB 900
        Ibus4fc = I1#
        '*******************************************


        '*******************************************    
        'BUS 2 Battery Output
        'BUS1
        V2# = Vr / 83.33334
        V3# = (switch(15, 5) * switch(17, 5)) * Vfc
        V1# = (switch(15, 5) * switch(17, 5)) * Vb1
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R3# = source(2, 1)
        R1# = source(3, 1)
        V4# = Vb3 * link / 833.3334
        V5# = VrA * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt / 6944.445
        GOSUB 900
        Ibus1b1 = I1#

        'BUS2
        V2# = Vr * (switch(15, 5) * switch(17, 5)) / 83.33334
        V3# = Vfc
        V1# = Vb1
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R3# = source(2, 1)
        R1# = source(3, 1)
        V4# = Vb3 * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        V5# = VrA * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt1
        GOSUB 900
        Ibus2b1 = I1#

        'BUS3
        V2# = Vr * (switch(15, 5) * switch(17, 5) * switch(16, 5)) / 83.33334
        V3# = Vfc * switch(16, 5)
        V1# = Vb1 * switch(16, 5)
        IF V2# = 0 THEN R2# = 0 ELSE R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5))) / 6944.445
        R3# = source(2, 1)
        R1# = source(3, 1)
        V4# = Vb3 * switch(16, 5) * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        V5# = VrA * switch(16, 5) * (switch(15, 5) * switch(17, 5)) * link / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt2
        GOSUB 900
        Ibus3b1 = I1#

        'BUS4
        V2# = Vr * link / 83.33334
        V3# = Vfc * (switch(15, 5) * switch(17, 5)) * link
        V1# = Vb1 * (switch(15, 5) * switch(17, 5)) * link
        IF V2# = 0 THEN R2# = 0 ELSE R2# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) / 6944.445
        R3# = source(2, 1)
        R1# = source(3, 1)
        V4# = Vb3 / 833.3334
        V5# = VrA / 833.3334
        R4# = source(4, 1) / 694444.5
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5))) / 694444.5
        R6# = Rt4 / 694444.5
        GOSUB 900
        Ibus4b1 = I1#
        '*******************************************
       
        '*******************************************
        'AYSE Reactor Output
        'BUS1
        V5# = Vr * 10
        V2# = (switch(15, 5) * switch(17, 5)) * Vfc * 833.3334
        V3# = (switch(15, 5) * switch(17, 5)) * Vb1 * 833.3334
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V4# = Vb3 * link
        V1# = VrA * link
        R4# = source(4, 1)
        IF V1# = 0 THEN R1# = 100000 ELSE R1# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt * 100
        GOSUB 900
        Ibus1A = I1#

      
        'BUS2
        V5# = Vr * (switch(15, 5) * switch(17, 5)) * 10
        V2# = Vfc * 833.3334
        V3# = Vb1 * 833.3334
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V4# = Vb3 * (switch(15, 5) * switch(17, 5)) * link
        V1# = VrA * (switch(15, 5) * switch(17, 5)) * link
        R4# = source(4, 1)
        IF V1# = 0 THEN R1# = 100000 ELSE R1# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt1 * 694444.5
        GOSUB 900
        Ibus2A = I1#
        
        'LOCATE 23, 1: PRINT USING "##.####^^^^"; V5#; V2#; V3#; V4#; V1#;
        'LOCATE 24, 1: PRINT USING "##.####^^^^"; R5#; R2#; R3#; R4#; R1#; R6#;
        'LOCATE 25, 1: PRINT USING "##.####^^^^"; I1#;
       

        'BUS3
        V5# = Vr * switch(15, 5) * switch(17, 5) * switch(16, 5) * 10
        V2# = Vfc * switch(16, 5) * 833.3334
        V3# = Vb1 * switch(16, 5) * 833.3334
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V4# = Vb3 * switch(15, 5) * switch(17, 5) * switch(16, 5) * link
        V1# = VrA * switch(15, 5) * switch(17, 5) * switch(16, 5) * link
        R4# = source(4, 1)
        IF V1# = 0 THEN R1# = 100000 ELSE R1# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt2 * 694444.5
        GOSUB 900
        Ibus3A = I1#


        'BUS4
        V5# = Vr * link * 10
        V2# = Vfc * 833.3334 * link * (switch(15, 5) * switch(17, 5))
        V3# = Vb1 * 833.3334 * link * (switch(15, 5) * switch(17, 5))
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V4# = Vb3
        V1# = VrA
        R4# = source(4, 1)
        IF V1# = 0 THEN R1# = 100000 ELSE R1# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt4
        GOSUB 900
        Ibus4A = I1#
        '*******************************************

        '*******************************************
        'BATT 3 Output
        'BUS1
        V5# = Vr * 10
        V2# = (switch(15, 5) * switch(17, 5)) * Vfc * 833.3334
        V3# = (switch(15, 5) * switch(17, 5)) * Vb1 * 833.3334
        IF V5# = 0 THEN R5# = 100000 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V1# = Vb3 * link
        V4# = VrA * link
        R1# = source(4, 1)
        IF V4# = 0 THEN R4# = 100000 ELSE R4# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt * 100
        GOSUB 900
        Ibus1b3 = I1#
     
        'BUS2
        V5# = Vr * (switch(15, 5) * switch(17, 5)) * 10
        V2# = Vfc * 833.3334
        V3# = Vb1 * 833.3334
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V1# = Vb3 * (switch(15, 5) * switch(17, 5)) * link
        V4# = VrA * (switch(15, 5) * switch(17, 5)) * link
        R1# = source(4, 1)
        IF V4# = 0 THEN R4# = 100000 ELSE R4# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt1 * 694444.5
        GOSUB 900
        Ibus2b3 = I1#
      

        'BUS3
        V5# = Vr * switch(15, 5) * switch(17, 5) * switch(16, 5) * 10
        V2# = Vfc * switch(16, 5) * 833.3334
        V3# = Vb1 * switch(16, 5) * 833.3334
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V1# = Vb3 * switch(15, 5) * switch(17, 5) * switch(16, 5) * link
        V4# = VrA * switch(15, 5) * switch(17, 5) * switch(16, 5) * link
        R1# = source(4, 1)
        IF V4# = 0 THEN R4# = 100000 ELSE R4# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt2 * 694444.5
        GOSUB 900
        Ibus3b3 = I1#


        'BUS4
        V5# = Vr * link * 10
        V2# = Vfc * 833.3334 * link * (switch(15, 5) * switch(17, 5))
        V3# = Vb1 * 833.3334 * link * (switch(15, 5) * switch(17, 5))
        IF V5# = 0 THEN R5# = 0 ELSE R5# = source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)) * 100
        R2# = source(2, 1) * 694444.5
        R3# = source(3, 1) * 694444.5
        V1# = Vb3
        V4# = VrA
        R1# = source(4, 1)
        IF V4# = 0 THEN R4# = 100000 ELSE R4# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        R6# = Rt4
        GOSUB 900
        Ibus4b3 = I1#
        '*******************************************
        EL(11) = Ibus1R + ((Ibus1fc + Ibus1b1) / 83.33334) + ((Ibus1A + Ibus1b3) * 10)
        EL(12) = (Ibus2R * 83.33334) + Ibus2fc + Ibus2b1 + ((Ibus2A + Ibus2b3) * 833.3334)
        EL(13) = (Ibus3R * 83.33334) + Ibus3fc + Ibus3b1 + ((Ibus3A + Ibus3b3) * 833.3334)
        EL(14) = (Ibus4R / 10) + ((Ibus4fc + Ibus4b1) / 833.3334) + ((Ibus4A + Ibus4b3))
        EL(1) = Ibus1R + Ibus2R + Ibus3R + Ibus4R
        EL(2) = Ibus1fc + Ibus2fc + Ibus3fc + Ibus4fc
        EL(3) = Ibus1b1 + Ibus2b1 + Ibus3b1 + Ibus4b1
        EL(4) = Ibus1b3 + Ibus2b3 + Ibus3b3 + Ibus4b3
        EL(5) = Ibus1A + Ibus2A + Ibus3A + Ibus4A
        R2# = (source(1, 1) * 2 / (.00001 + switch(38, 5) + switch(39, 5)))
        V1out = Vr - (EL(1) * R2#)
        V2out = Vfc - (EL(2) * source(2, 1))
        V3out = Vb1 - (EL(2) * source(2, 1))
        V4out = Vb3 - (EL(4) * source(4, 1))
        R2# = (source(5, 1) * 2 / (.00001 + switch(43, 5) + switch(44, 5)))
        V5out = VrA - (EL(5) * R2#)
        'LOCATE 20, 30: PRINT V4out; EL(4); Rt4;
        IF EL(11) = 0 THEN EL(6) = Vbus1max ELSE EL(6) = (V1out * Ibus1R / EL(11)) + (V2out * Ibus1fc / EL(11)) + (V3out * Ibus1b1 / EL(11)) + (V4out * Ibus1b3 / EL(11)) + (V5out * Ibus1A / EL(11))
        IF EL(12) = 0 THEN EL(7) = Vbus2max ELSE EL(7) = (V1out * Ibus2R / EL(12)) + (V2out * Ibus2fc / EL(12)) + (V3out * Ibus2b1 / EL(12)) + (V4out * Ibus2b3 / EL(12)) + (V5out * Ibus2A / EL(12))
        IF EL(13) = 0 THEN EL(8) = Vbus3max ELSE EL(8) = (V1out * Ibus3R / EL(13)) + (V2out * Ibus3fc / EL(13)) + (V3out * Ibus3b1 / EL(13)) + (V4out * Ibus3b3 / EL(13)) + (V5out * Ibus3A / EL(13))
        IF EL(14) < .00000001# THEN EL(9) = Vbus4max ELSE EL(9) = (V1out * Ibus4R / EL(14)) + (V2out * Ibus4fc / EL(14)) + (V3out * Ibus4b1 / EL(14)) + (V4out * Ibus4b3 / EL(14)) + (V5out * Ibus4A / EL(14))
        IF EL(11) < 0 THEN EL(11) = 0
        IF EL(12) < 0 THEN EL(12) = 0
        IF EL(13) < 0 THEN EL(13) = 0
        IF EL(14) < 0 THEN EL(14) = 0
        IF EL(6) < 0 THEN EL(6) = 0
        IF EL(7) < 0 THEN EL(7) = 0
        IF EL(8) < 0 THEN EL(8) = 0
        IF EL(9) < 0 THEN EL(9) = 0
        'IF EL(9) < 9000 THEN switch(29, 5) = 0: switch(30, 5) = 0: switch(31, 5) = 0: switch(32, 5) = 0: switch(33, 5) = 0: switch(56, 5) = 0: switch(26, 5) = 1

        IF switch(18, 5) = 0 AND BattAH(1) < 10000 THEN BattAH(1) = BattAH(1) + (DELtime# * EL(7) / 2500)
        BattAH(1) = BattAH(1) - (DELtime# * EL(3) / 3600)
        IF BattAH(1) < 0 THEN BattAH(1) = 0
        IF source(3, 2) = 1 THEN BattAH(1) = 0

        IF switch(26, 5) = 0 AND BattAH(3) < 99 THEN BattAH(3) = BattAH(3) + (DELtime# * EL(9) / 2500000)
        BattAH(3) = BattAH(3) - (DELtime# * EL(4) / 3600)
        IF BattAH(3) < 0 THEN BattAH(3) = 0
        IF source(4, 2) = 1 THEN BattAH(3) = 0
       
        IF switch(16, 5) = 1 AND EL(7) < 90 AND BattAH(2) > 0 THEN switch(16, 5) = 0
        IF switch(16, 5) = 1 AND BattAH(2) < 9999 THEN BattAH(2) = BattAH(2) + (DELtime# * EL(8) / 2500)
        IF switch(16, 5) = 1 THEN 202
        IF BattAH(2) > 0 THEN EL(8) = 120: Is6 = 120 / Rt2: EL(13) = Is6: BattAH(2) = BattAH(2) - (DELtime# * Is6 / 3600) ELSE EL(8) = 0: Is6 = 0: EL(13) = 0
        IF BattAH(2) < 0 THEN BattAH(2) = 0
202     RETURN

300     IF switch(4, 5) = 0 THEN Vdel1 = 10000 ELSE Vdel1 = 10000 - EL(6)
        IF switch(5, 5) = 0 THEN Vdel2 = 10000 ELSE Vdel2 = 10000 - EL(6)
        Ireactor = 10000 * Hreactor
        IrcNEEDED# = (EL(1) * .001)
        'LOCATE 21, 20: PRINT USING "####.#########"; Ireactor, IrcNEEDED#;
        IF Ireactor + EL(1) > 0 AND IrcNEEDED# < 1 THEN IrcNEEDED# = 1#
        IrcNEEDED# = IrcNEEDED# + Ireactor
        IrcGEN# = ((EL(6)) / switch(4, 6)) + ((EL(6)) / switch(5, 6)) + (switch(0, 5) * EL(6) * Hreactor)
        IF IrcGEN# < IrcNEEDED# THEN RCcap = RCcap + (IrcGEN# - IrcNEEDED#)
        'LOCATE 21, 25: PRINT USING "#######.#####"; IrcGEN#; IrcNEEDED#; Ireactor;
        IF IrcGEN# < IrcNEEDED AND switch(0, 8) > 30 THEN 301
        IF switch(4, 5) + switch(5, 5) > 0 AND RCcap < 2000 THEN RCcap = RCcap + (EL(6) / 1000)
301     RETURN


900     'LOCATE 22, 1: PRINT USING "######"; V1#; V2#; V3#; V4#; V5#;
        'LOCATE 23, 1: PRINT USING "#######.#####"; R1#; R2#; R3#; R4#; R5#; R6#;
        IF V1# = 0 THEN I1# = 0: GOTO 901
        Rdenom# = 0 - R1# - R6#
        IF V2# > 0 THEN Rdenom# = Rdenom# - (R1# * R6# / R2#)
        IF V3# > 0 THEN Rdenom# = Rdenom# - (R1# * R6# / R3#)
        IF V4# > 0 THEN Rdenom# = Rdenom# - (R1# * R6# / R4#)
        IF V5# > 0 THEN Rdenom# = Rdenom# - (R1# * R6# / R5#)
        I1# = 0 - V1#
        IF V2# > 0 THEN I1# = I1# - (R6# * V1# / R2#)
        IF V2# > 0 THEN I1# = I1# + (R6# * V2# / R2#)
        IF V3# > 0 THEN I1# = I1# - (R6# * V1# / R3#)
        IF V3# > 0 THEN I1# = I1# + (R6# * V3# / R3#)
        IF V4# > 0 THEN I1# = I1# - (R6# * V1# / R4#)
        IF V4# > 0 THEN I1# = I1# + (R6# * V4# / R4#)
        IF V5# > 0 THEN I1# = I1# - (R6# * V1# / R5#)
        IF V5# > 0 THEN I1# = I1# + (R6# * V5# / R5#)

        I1# = I1# / Rdenom#
        P1# = R1# * I1# * I1#
        Vout# = V1# - (R1# * I1#)
901     RETURN

800     OPEN "R", #1, "orb5rEs.RND", 412
        inpSTR$=space$(412)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 412 then return
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$<>chkCHAR2$ then return
        k = 2
        FOR i = 1 TO 5
         SOURCEs(i, 1)=cvd(mid$(inpSTR$,k,8)):k=k+8
         SOURCEs(i, 2)=cvd(mid$(inpSTR$,k,8)):k=k+8
         z=cvd(mid$(inpSTR$,k,8)):k=k+8
         IF z = 1 THEN source(i, 2) = 0
        NEXT i
        FOR i = 1 TO 47
         DEVICEs(i)=cvi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        FOR i = 1 TO 64
         SWITCHs%(i)=cvi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        SWITCHs%(15) = SWITCHs%(15) + (4 * SWITCHs%(24))
        SWITCHs%(52) = SWITCHs%(52) + (4096 * SWITCHs%(53))
        FOR i = 1 TO 4
         z=cvs(mid$(inpSTR$,k,4)):k=k+4
         SHORTc(i) = 10 ^ z
         IF (i AND DEVICEs(43)) = i THEN coolant(i, 3) = 0
        NEXT i
        HABfuelleak=cvs(mid$(inpSTR$,k,4)):k=k+4
        AYSEfuelleak=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(14)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(15)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(16)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(17)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(18)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(19)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(20)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(21)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(22)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(23)=cvs(mid$(inpSTR$,k,4)):k=k+4
        Zvar#(26)=cvs(mid$(inpSTR$,k,4)):k=k+4
        IF SWITCHs%(63) = 2 THEN SRBused = 1
        IF SWITCHs%(63) = 1 THEN SRBused = 0
        RETURN

810     k=1
812     OPEN "R", #1, "OSBACKUP.RND", 1427
        inpSTR$=space$(1427)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1427 then 811
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        ORBITversion$=mid$(inpSTR$, 2, 7)
        if ORBITversion$<>"ORBIT5S" then 811
        if chkCHAR1$=chkCHAR2$ then 813
        k=k+1
        if k<3 then 812 else 811 

813     k=2+15
        if OLDchkCHAR1$=chkCHAR1$ then orbTELEMflag=4 else orbTELEMflag=0
        OLDchkCHAR1$=chkCHAR1$
        Zvar#(25) = cvs(mid$(inpSTR$,k,4)):k=k+4
        k=k+68
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

        Accel# = 5
        OLDtime# = NEWtime#
        NEWtime# = sec + (min * 60#) + (hr * 3600#) + (day * 24# * 3600#) + (year * 365# * 24# * 3600#)
        DELtime# = NEWtime# - OLDtime#
        'IF DELtime# > 60 THEN CLS : PRINT DELtime#: z$ = INPUT$(1)
        IF DELtime# < 0 THEN DELtime# = 0
        IF OLDtime# = 0 THEN DELtime# = 0
        Zvar#(25) = ABS(Zvar#(25))
811     RETURN




830     OPEN "R", #1, "ORBITSSE.RND", 1159
        inpSTR$=space$(1159)
        GET #1, 1, inpSTR$
        close #1
        if len(inpSTR$) <> 1159 then 831
        chkCHAR1$=left$(inpSTR$,1)
        chkCHAR2$=right$(inpSTR$,1)
        if chkCHAR1$<>chkCHAR2$ then 831
        k = 2
        if OLDchkCHAR2$=chkCHAR1$ then engTELEMflag=4 else engTELEMflag=0
        OLDchkCHAR2$=chkCHAR1$
        FOR i = 1 TO 26
         Zvar#(i)=CVD(mid$(inpSTR$,k,8)):k=k+8
        NEXT i
        PARA = SGN(2 and Zvar#(10))
        SRB = SGN(4 and Zvar#(10))
        k=k+1
        FOR i = 1 TO 15
         EL(i)=CVS(mid$(inpSTR$,k,4)):k=k+4
        NEXT i
        FOR i = 0 TO 65
         switch(i, 5)=CVi(mid$(inpSTR$,k,2)):k=k+2
         switch(i, 8)=CVs(mid$(inpSTR$,k,4)):k=k+4
         switch(i, 11)=CVi(mid$(inpSTR$,k,2)):k=k+2
        NEXT i
        FOR i = 1 TO 10
         coolantPUMP(i)=CVs(mid$(inpSTR$,k,4)):k=k+4
         FOR j = 0 TO 3
          coolant(i, j)=CVs(mid$(inpSTR$,k,4)):k=k+4
          RAD(i, j)=CVs(mid$(inpSTR$,k,4)):k=k+4
         NEXT j
        NEXT i
        RCcap = switch(57, 11)
831     RETURN


850     heat = power * switch(dev, 12)
852     'COLOR 7, 0: LOCATE 1, dev + 1: PRINT "*"
        IF (1 AND switch(dev, 11)) = 1 THEN coolant1 = 1 ELSE coolant1 = 1000
        IF (2 AND switch(dev, 11)) = 2 THEN coolant2 = 1 ELSE coolant2 = 1000
        IF (32 AND switch(dev, 11)) = 32 THEN coolant3 = 1 ELSE coolant3 = 1000
        heat = heat * (1 + ((960 AND SWITCHs%(dev)) / 1000))
        delTEMP1 = switch(dev, 13) * (switch(dev, 8) ^ 2)
        IF coolant1 < 1000 THEN delTEMP2 = (switch(dev, 15) / (coolant1 + coolant(1, 0))) * (switch(dev, 8) ^ 2) ELSE delTEMP2 = 0
        IF coolant2 < 1000 THEN delTEMP3 = (switch(dev, 14) / (coolant2 + coolant(2, 0))) * (switch(dev, 8) ^ 2) ELSE delTEMP3 = 0
        IF habENG = 1 THEN delTEMP4 = (.1 * (switch(dev, 15) + switch(dev, 15)) * ((1 + pressure) ^ 3 - 1) * (switch(dev, 8) ^ 2)) ELSE delTEMP4 = 0
        IF coolant3 < 1000 THEN delTEMP5 = (switch(dev, 15) / (coolant3 + coolant(3, 0))) * (switch(dev, 8) ^ 2) ELSE delTEMP5 = 0
        switch(dev, 8) = switch(dev, 8) + heat - delTEMP1
        TEMPmin = switch(dev, 8) - switch(dev, 16)
        IF TEMPmin < 0 THEN TEMPmin = 0
        delTEMPtotal = delTEMP2 + delTEMP3 + delTEMP4 + delTEMP5
        'IF delTEMPtotal = 0 THEN 851
        IF TEMPmin < delTEMPtotal THEN delTEMP2 = delTEMP2 * (TEMPmin / delTEMPtotal): delTEMP3 = delTEMP3 * (TEMPmin / delTEMPtotal): delTEMP4 = delTEMP4 * (TEMPmin / delTEMPtotal): delTEMP5 = delTEMP5 * (TEMPmin / delTEMPtotal)
        dem = (switch(dev, 14) + switch(dev, 15))
        IF dem = 0 THEN factor1 = 1: factor2 = 1 ELSE factor1 = switch(dev, 14) / dem: factor2 = switch(dev, 15) / dem
        'IF dev = 7 THEN LOCATE 1, 40: PRINT USING "##.#####"; dev; delTEMP2; delTEMP3;
        switch(dev, 8) = switch(dev, 8) - delTEMP3
        switch(dev, 8) = switch(dev, 8) - delTEMP2
        switch(dev, 8) = switch(dev, 8) - delTEMP4
        switch(dev, 8) = switch(dev, 8) - delTEMP5
        coolant(1, 0) = coolant(1, 0) + (delTEMP2 * factor1)
        coolant(2, 0) = coolant(2, 0) + (delTEMP3 * factor2)
        coolant(3, 0) = coolant(3, 0) + (delTEMP5 * factor2)
        IF switch(dev, 8) > 999 THEN switch(dev, 8) = 999
        IF switch(dev, 8) < 0 THEN switch(dev, 8) = 0
853     IF switch(dev, 8) < switch(dev, 16) THEN clrf = 1 ELSE clrf = 10
        IF switch(dev, 8) > 90 THEN clrf = 14
        IF switch(dev, 8) > 100 THEN clrf = 12
851     RETURN
       
860     FOR i = 1 TO 3
         'LOCATE i + 22, 30: PRINT coolant(i, 0);
         coolant(i, 1) = 0
         IF DEVICEs(i) = 2 THEN coolantPUMP(i) = (1 AND coolantPUMP(i))
         IF DEVICEs(i + 6) = 2 THEN coolantPUMP(i) = (2 AND coolantPUMP(i))
        NEXT i
        'LOCATE 23, 23: PRINT USING "###.#"; coolant(1, 0);
        'LOCATE 24, 23: PRINT USING "###.#"; coolant(2, 0);
        'LOCATE 25, 23: PRINT USING "###.#"; coolant(3, 0);
        IF EL(6) < 9000 THEN coolantPUMP(1) = 1 AND coolantPUMP(1): coolantPUMP(2) = 1 AND coolantPUMP(2)
        IF EL(7) < 90 THEN coolantPUMP(1) = 2 AND coolantPUMP(1): coolantPUMP(2) = 2 AND coolantPUMP(2)
        IF EL(9) < 90000 THEN coolantPUMP(3) = 0
        FOR i = 1 TO 8
         IF ((2 ^ (2 + ((i - 1) * 3))) AND SWITCHs%(64)) > 0 THEN 861
         coolant(RAD(i, 1), 1) = coolant(RAD(i, 1), 1) + ((1 + (pressure * 3) ^ 2) * coolant(RAD(i, 1), 2) * .01 * RAD(i, 0) * coolant(RAD(i, 1), 0) ^ 2)
861     NEXT i
        FOR i = 1 TO 3
         coolant(i, 0) = coolant(i, 0) - coolant(i, 1)
         IF coolant(i, 0) > 999 THEN coolant(i, 0) = 999
         IF coolant(i, 0) < 0 THEN coolant(i, 0) = 0
        NEXT i
        'LOCATE 23, 28: PRINT USING "###.#"; coolant(1, 1);
        'LOCATE 24, 28: PRINT USING "###.#"; coolant(2, 1);
        'LOCATE 25, 28: PRINT USING "###.#"; coolant(3, 1);
        'LOCATE 23, 33: PRINT USING "###.#"; coolant(1, 0);
        'LOCATE 24, 33: PRINT USING "###.#"; coolant(2, 0);
        'LOCATE 25, 33: PRINT USING "###.#"; coolant(3, 0);
        RETURN


870     FOR dev = 6 TO 13
         IF switch(dev, 11) > 5 THEN 871
         switch(dev, 11) = 3
871     NEXT dev
        RETURN


880     IF Zvar#(13) = 150 THEN 881
        FOR i = 6 TO 13
         IF (4096 AND SWITCHs%(i)) = 4096 THEN 882
         switch(i, 11) = switch(i, 11) + 1
         IF switch(i, 11) > 3 THEN switch(i, 11) = 0
882     NEXT i
        RETURN
881     FOR i = 29 TO 33
         IF (4096 AND SWITCHs%(i)) = 4096 THEN 883
         switch(i, 11) = switch(i, 11) + 1
         IF switch(i, 11) = 3 THEN switch(i, 11) = 0
883     NEXT i
        RETURN


2000    LOCATE 25, 1: PRINT ERR, ERL;
        z$=input$(1)
        END


