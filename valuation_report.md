# 2026 valuation report

## Detected scoring and league config

| setting | value |
|---|---|
| passing yards per point | 25 (0.04 pts/yard) |
| passing TD | 4.0 |
| interception | -2.0 |
| rushing/receiving yards per point | 10 (0.1 pts/yard) |
| rushing/receiving TD | 6.0 |
| reception | 0.5 (half-PPR) |
| fumble lost | -2.0 |
| yardage/big-play bonuses | none (`BONUSES={}`) |
| 2-pt / return TD | 0 (not in CFBD extract) |
| fantasy regular-season weeks | 12 |
| playoff weeks | 0 |
| teams | 14 |
| lineup | 2QB / 2RB / 2WR / 2 FLEX ['RB', 'TE', 'WR'] / 1K / 1 D/ST |
| required TE | 0 |
| expected QBs rostered per team | 3.0 (default 42 total) |
| named-QB prior | 0.9 × unmodified QB29 |

## Starter composition

{
  "n_qb": 28,
  "n_skill": 84,
  "n_rb": 55,
  "n_wr": 28,
  "n_te": 1
}

FLEX replacement (first excluded skill): 159.2
QB cutoffs (first player outside N rostered): 28→245.1, 35→228.3, 42→224.0
TE in the 84 skill starters: 1 (optional FLEX only)

## 28 / 35 / 42 QB sensitivity (top 15 QBs by draft-adjusted value)

 rank                name team  projected_points_if_active  starter_vorp  qb35_adjusted_value  qb42_adjusted_value  draft_adjusted_value
    2         Byrum Brown  AUB                       313.9          68.8                 85.6                 89.9                  89.9
    3      Conner Weigman  HOU                       312.1          67.0                 83.8                 88.1                  88.1
    4        Brad Jackson TXST                       310.0          64.9                 81.7                 86.0                  86.0
   11       Devon Dampier UTAH                       286.4          41.3                 58.1                 62.4                  62.4
   12       Avery Johnson  KSU                       280.3          35.2                 52.0                 56.3                  56.3
   13         Marcel Reed TA&M                       279.9          34.8                 51.6                 55.9                  55.9
   17       Bryson Barnes  USU                       273.4          28.3                 45.1                 49.4                  49.4
   21       Colton Joseph  WIS                       269.6          24.5                 41.3                 45.6                  45.6
   28      Bear Bachmeier  BYU                       260.9          15.8                 32.6                 36.9                  36.9
   31  Trinidad Chambliss MISS                       259.7          14.6                 31.4                 35.7                  35.7
   34      Nick Minicucci  DEL                       257.9          12.8                 29.6                 33.9                  33.9
   37 Demond Williams Jr. WASH                       257.7          12.6                 29.4                 33.7                  33.7
   39         Liam Szarka   AF                       257.2          12.1                 28.9                 33.2                  33.2
   41        Arch Manning  TEX                       256.9          11.8                 28.6                 32.9                  32.9
   43          Broc Lowry  WMU                       255.4          10.3                 27.1                 31.4                  31.4

## Before / after top 150

Old board top 15:

 rank               name position  proj_points  draft_value
    1         Kewan Lacy       RB        252.6         95.1
    2          LJ Martin       RB        240.4         82.9
    3           Cam Cook       RB        231.2         73.7
    4        Byrum Brown       QB        313.9         68.8
    5     Conner Weigman       QB        312.1         67.0
    6      DeSean Bishop       RB        224.2         66.7
    7       Evan Dickens       RB        224.1         66.6
    8     Jai'Den Thomas       RB        223.5         66.0
    9       Brad Jackson       QB        310.0         64.9
   10        Beau Sparks       WR        214.9         63.4
   11     Antwan Raymond       RB        213.9         56.4
   12 Will Henderson III       RB        213.4         55.9
   13     Jeremiah Smith       WR        207.1         55.6
   14        Ahmad Hardy       RB        211.6         54.1
   15     Braylon Staley       WR        200.5         49.0

Tuned board top 15 (old_rank is the previous overall rank):

 rank                  name team position pos_rank  proj_points  managed_vorp  starter_vorp  draft_adjusted_value  role  old_rank
    1            Kewan Lacy MISS       RB      RB1        252.6          93.4          93.4                  93.4  1.00         1
    2           Byrum Brown  AUB       QB      QB1        313.9          68.8          68.8                  89.9  1.00         4
    3        Conner Weigman  HOU       QB      QB2        312.1          67.0          67.0                  88.1  1.00         5
    4          Brad Jackson TXST       QB      QB3        310.0          64.9          64.9                  86.0  1.00         9
    5             LJ Martin  BYU       RB      RB2        240.4          81.2          81.2                  81.2  1.00         2
    6           Ahmad Hardy  MIZ       RB      RB3        211.6          78.9          94.7                  78.9  1.00        14
    7              Cam Cook  WVU       RB      RB4        231.2          72.0          72.0                  72.0  1.00         3
    8         DeSean Bishop TENN       RB      RB5        224.2          65.0          65.0                  65.0  1.00         6
    9          Evan Dickens   BC       RB      RB6        224.1          64.9          64.9                  64.9  1.00         7
   10        Jai'Den Thomas UNLV       RB      RB7        223.5          64.3          64.3                  64.3  1.00         8
   11         Devon Dampier UTAH       QB      QB4        286.4          41.3          41.3                  62.4  1.00        21
   12         Avery Johnson  KSU       QB      QB5        280.3          35.2          35.2                  56.3  1.00        35
   13           Marcel Reed TA&M       QB      QB6        279.9          34.8          34.8                  55.9  1.00        36
   14           Beau Sparks TXST       WR      WR1        214.9          55.7          63.4                  55.7  1.00        10
   15        Antwan Raymond RUTG       RB      RB8        213.9          54.7          54.7                  54.7  1.00        11
   16    Will Henderson III UTSA       RB      RB9        213.4          54.2          54.2                  54.2  1.00        12
   17         Bryson Barnes  USU       QB      QB7        273.4          28.3          28.3                  49.4  1.00        42
   18        Jeremiah Smith  OSU       WR      WR2        207.1          47.9          55.6                  47.9  1.00        13
   19             CJ Miller  TOL       RB     RB10        205.6          46.4          46.4                  46.4  1.00      3509
   20       Wayshawn Parker UTAH       RB     RB11        205.5          46.3          46.3                  46.3  1.00        17
   21         Colton Joseph  WIS       QB      QB8        269.6          24.5          24.5                  45.6  1.00        48
   22         Caleb Hawkins OKST       RB     RB12        202.6          43.4          43.4                  43.4  1.00        18
   23    Rodney Hammond Jr.  SAC       RB     RB13        201.0          41.8          41.8                  41.8  1.00        20
   24        Braylon Staley TENN       WR      WR3        200.5          41.3          49.0                  41.3  1.00        15
   25     Sedrick Alexander  VAN       RB     RB14        198.8          39.6          39.6                  39.6  1.00        22
   26          Jeremy Payne  TCU       RB     RB15        197.7          38.5          38.5                  38.5  1.00        24
   27           Cam Edwards  MSU       RB     RB16        197.0          37.8          37.8                  37.8  1.00        25
   28        Bear Bachmeier  BYU       QB      QB9        260.9          15.8          15.8                  36.9  1.00        61
   29        Fluff Bothwell MSST       RB     RB17        195.6          36.4          36.4                  36.4  1.00        28
   30         Mike Matthews TENN       WR      WR4        195.1          35.9          43.6                  35.9  1.00        19
   31    Trinidad Chambliss MISS       QB     QB10        259.7          14.6          14.6                  35.7  1.00        62
   32            Bo Jackson  OSU       RB     RB18        194.8          35.6          35.6                  35.6  1.00        30
   33       Aneyas Williams   ND       RB     RB19        193.4          34.2          34.2                  34.2  1.00        32
   34        Nick Minicucci  DEL       QB     QB11        257.9          12.8          12.8                  33.9  1.00        64
   35       J'Koby Williams  TTU       RB     RB20        193.1          33.9          33.9                  33.9  0.85       110
   36        Cameron Dickey  TTU       RB     RB21        193.1          33.9          33.9                  33.9  0.85       109
   37   Demond Williams Jr. WASH       QB     QB12        257.7          12.6          12.6                  33.7  1.00        65
   38         Nate Sheppard DUKE       RB     RB22        192.8          33.6          33.6                  33.6  1.00        34
   39           Liam Szarka   AF       QB     QB13        257.2          12.1          12.1                  33.2  1.00        68
   40          Mario Craver TA&M       WR      WR5        192.3          33.1          40.8                  33.1  1.00        23
   41          Arch Manning  TEX       QB     QB14        256.9          11.8          11.8                  32.9  1.00        69
   42               KJ Duff RUTG       WR      WR6        191.0          31.8          39.5                  31.8  1.00        26
   43            Broc Lowry  WMU       QB     QB15        255.4          10.3          10.3                  31.4  1.00        73
   44        Caleb Komolafe   NU       RB     RB23        190.5          31.3          31.3                  31.3  1.00        37
   45         Easton Messer  FAU       WR      WR7        190.4          31.2          38.9                  31.2  1.00        27
   46       Gunner Stockton  UGA       QB     QB16        254.9           9.8           9.8                  30.9  1.00        74
   47           Noah Fifita ARIZ       QB     QB17        254.7           9.6           9.6                  30.7  1.00        75
   48           John Mateer   OU       QB     QB18        254.4           9.3           9.3                  30.4  1.00        76
   49         Malachi Toney  MIA       WR      WR8        189.4          30.2          37.9                  30.2  1.00        29
   50     L.J. Phillips Jr. IOWA       RB     RB24        189.2          30.0          30.0                  30.0  0.98        38
   51          Amare Thomas  HOU       WR      WR9        188.3          29.1          36.8                  29.1  1.00        31
   52         Jaylen Raynor  ISU       QB     QB19        252.5           7.4           7.4                  28.5  1.00        80
   53             Nick Osho  UNT       RB     RB25        187.6          28.4          28.4                  28.4  1.00        39
   54               CJ Carr   ND       QB     QB20        251.6           6.5           6.5                  27.6  1.00        81
   55         Jalen Buckley  WMU       RB     RB26        186.5          27.3          27.3                  27.3  1.00        40
   56    Alonza Barnett III  UCF       QB     QB21        251.1           6.0           6.0                  27.1  0.98        83
   57           Jadan Baugh  FLA       RB     RB27        185.5          26.3          26.3                  26.3  1.00        43
   58          Javen Jacobs  USU       RB     RB28        185.4          26.2          26.2                  26.2  1.00        44
   59     Anthony Colandrea  NEB       QB     QB22        250.0           4.9           4.9                  26.0  1.00        86
   60         Maddux Madsen BOIS       QB     QB23        249.4           4.3           4.3                  25.4  1.00        89
   61        Caden Veltkamp  FAU       QB     QB24        248.9           3.8           3.8                  24.9  1.00        91
   62           Isaac Brown  LOU       RB     RB29        183.5          24.3          24.3                  24.3  1.00        45
   63           Dylan Riley BOIS       RB     RB30        183.1          23.9          23.9                  23.9  0.85       137
   64           Sire Gaines BOIS       RB     RB31        183.1          23.9          23.9                  23.9  0.85       138
   65          Tyler Hughes  WYO       QB     QB25        247.8           2.7           2.7                  23.8  0.99       100
   66          Duncan Brune OHIO       RB     RB32        183.0          23.8          23.8                  23.8  1.00        46
   67        Justice Haynes   GT       RB     RB33        182.4          23.2          23.2                  23.2  1.00        47
   68        Kamario Taylor MSST       QB     QB26        247.1           2.0           2.0                  23.1  0.96       104
   69          Julian Sayin  OSU       QB     QB27        246.8           1.7           1.7                  22.8  1.00       106
   70       Rueben Owens II TA&M       RB     RB34        181.9          22.7          22.7                  22.7  1.00        50
   71           Jordan Gant  AKR       RB     RB35        181.8          22.6          22.6                  22.6  1.00        51
   72           DJ McKinney TLSA       RB     RB36        181.5          22.3          22.3                  22.3  0.99        52
   73          Lucky Sutton SDSU       RB     RB37        181.0          21.8          21.8                  21.8  1.00        53
   74         Jayden Maiava  USC       QB     QB28        245.2           0.1           0.1                  21.2  1.00       112
   75        Mason McKenzie   BC       QB     QB29        245.1           0.0          -0.1                  21.1  0.82       113
   76        Jackson Harris  LSU       WR     WR10        180.3          21.1          28.8                  21.1  0.98        41
   77           Caden Creel JXST       QB     QB30        244.3          -0.8          -0.9                  20.3  1.00       121
   78          Will Hammond  TTU       QB     QB31        243.7          -1.4          -1.5                  19.7  0.95       123
   79        Jordon Davison  ORE       RB     RB38         99.1          19.5          39.0                  19.5  1.00       574
   80      Ja'Kyrian Turner PITT       RB     RB39        178.6          19.4          19.4                  19.4  1.00        56
   81            Joshua Dye MISS       RB     RB40        176.8          17.6          17.6                  17.6  0.92        57
   82         Rodney Nelson M-OH       RB     RB41        176.1          16.9          16.9                  16.9  0.70        58
   83            Ryan Wingo  TEX       WR     WR11        176.0          16.8          24.5                  16.8  1.00        49
   84         Darius Taylor MINN       RB     RB42        175.4          16.2          16.2                  16.2  1.00      3347
   85          Nate Frazier  UGA       RB     RB43        174.3          15.1          15.1                  15.1  1.00        60
   86       Skyler Locklear MOST       QB     QB32        238.8          -6.3          -6.4                  14.8  1.00       136
   87          Micahi Danzy  FSU       WR     WR12        173.6          14.4          22.1                  14.4  1.00        54
   88         Griffin Wilde   NU       WR     WR13        173.0          13.8          21.5                  13.8  1.00        55
   89          Cale Hellums ARMY       QB     QB33        236.7          -8.4          -8.5                  12.7  1.00       142
   90         Caden Pinnick  WSU       QB     QB34        236.6          -8.5          -8.6                  12.6  0.97       145
   91          Wayne Knight UCLA       RB     RB44        171.2          12.0          12.0                  12.0  1.00        63
   92         Carson Hansen  PSU       RB     RB45        169.9          10.7          10.7                  10.7  1.00        66
   93    Quintrevion Wisner  FSU       RB     RB46        168.5           9.3           9.3                   9.3  1.00        70
   94     Mark Fletcher Jr.  MIA       RB     RB47        167.8           8.6           8.6                   8.6  1.00        72
   95       Braxton Woodson NAVY       QB     QB35        228.5         -16.6         -16.7                   4.5  1.00       180
   96           Wyatt Young OKST       WR     WR14        163.7           4.5          12.2                   4.5  1.00        67
   97            Matt Vezza OHIO       QB     QB36        228.3         -16.8         -16.9                   4.3  1.00       181
   98       Landen Chambers  UCF       RB     RB48        163.0           3.8           3.8                   3.8  0.93        85
   99       Drew Mestemaker OKST       QB     QB37        227.1         -18.0         -18.1                   3.1  1.00       185
  100          Jordan Shipp  UNC       WR     WR15        162.2           3.0          10.7                   3.0  1.00        71
  101          Beau Pribula  UVA       QB     QB38        226.3         -18.8         -18.9                   2.3  0.96       190
  102          Kaden Feagin  ILL       TE      TE1        160.8           1.6           1.6                   1.6  1.00        33
  103  Kaden Shields-Dutton  FAU       RB     RB49        160.6           1.4           1.4                   1.4  0.98        95
  104        Pofele Ashlock  HAW       WR     WR16        160.5           1.3           9.0                   1.3  1.00        77
  105            Micah Ford STAN       RB     RB50        160.4           1.2           1.2                   1.2  1.00        97
  106      Ramone Green Jr. MOST       RB     RB51        160.4           1.2           1.2                   1.2  1.00        96
  107          Angel Flores  CMU       QB     QB39        225.1         -20.0         -20.1                   1.1  1.00       194
  108          Rayshon Luke FRES       RB     RB52        160.3           1.1           1.1                   1.1  1.00        98
  109    Anthony Reagan Jr.   UL       RB     RB53        160.3           1.1           1.1                   1.1  0.99        99
  110      Malik Washington   MD       QB     QB40        224.9         -20.2         -20.3                   0.9  1.00       196
  111          Sutton Smith  ARK       RB     RB54        159.7           0.5           0.5                   0.5  1.00       102
  112           Rocco Becht  PSU       QB     QB41        224.4         -20.7         -20.8                   0.4  1.00       198
  113         Jordan Napier SDSU       WR     WR17        159.5           0.3           8.0                   0.3  1.00        79
  114       Deuce Alexander MISS       WR     WR18        159.5           0.3           8.0                   0.3  1.00        78
  115        Kevin Jennings  SMU       QB     QB42        224.2         -20.9         -21.0                   0.2  1.00       199
  116          Cam Barfield  HAW       RB     RB55        159.3           0.1           0.1                   0.1  1.00       105
  117          Katin Houser  ILL       QB     QB43        224.0         -21.1         -21.2                   0.0  1.00       200
  118       Kenji Christian CONN       RB     RB56        159.2           0.0          -0.1                   0.0  1.00       107
  119     Chris Johnson Jr. CLEM       RB     RB57        159.2           0.0          -0.1                   0.0  1.00       108
  120           King Miller  USC       RB     RB58        158.6          -0.6          -0.7                  -0.6  0.84       223
  121         Taron Dickens  NIU       QB     QB44        223.2         -21.9         -22.0                  -0.8  0.95       205
  122        Waymond Jordan  USC       RB     RB59        157.9          -1.3          -1.4                  -1.3  0.86       260
  123           Daniel Hill  ALA       RB     RB60        157.7          -1.5          -1.6                  -1.5  1.00       111
  124             CJ Bailey NCSU       QB     QB45        222.4         -22.7         -22.8                  -1.6  1.00       209
  125         Danny Scudero COLO       WR     WR19        157.6          -1.6           6.1                  -1.6  1.00        82
  126       Jordan Marshall MICH       RB     RB61        157.5          -1.7          -1.8                  -1.7  0.70       114
  127      Bishop Davenport  USA       QB     QB46        222.2         -22.9         -23.0                  -1.8  1.00       211
  128         Micah Alejado  HAW       QB     QB47        222.2         -22.9         -23.0                  -1.8  1.00       212
  129          Jordan Dwyer  TCU       WR     WR20        157.4          -1.8           5.9                  -1.8  1.00        84
  130         Turbo Richard   IU       RB     RB62        157.2          -2.0          -2.1                  -2.0  1.00       118
  131        Lunch Winfield   UL       QB     QB48        221.7         -23.4         -23.5                  -2.3  1.00       213
  132     Telly Johnson Jr.  NIU       RB     RB63        156.7          -2.5          -2.6                  -2.5  1.00       120
  133     Keshaun Singleton  AUB       WR     WR21        156.4          -2.8           4.9                  -2.8  1.00        87
  134       Junior Sherrill  VAN       WR     WR22        156.0          -3.2           4.5                  -3.2  1.00        88
  135         Michael Allen  ECU       RB     RB64        155.8          -3.4          -3.5                  -3.4  0.95       124
  136         Duce Robinson  FSU       WR     WR23        155.7          -3.5           4.2                  -3.5  1.00        90
  137            Nico Brown STAN       WR     WR24        155.2          -4.0           3.7                  -4.0  0.96        92
  138          Jaden Barnes  CLT       WR     WR25        155.1          -4.1           3.6                  -4.1  1.00        93
  139 Ryan Coleman-Williams  ALA       WR     WR26        154.7          -4.5           3.2                  -4.5  1.00        94
  140            Bill Davis   VT       RB     RB65        153.9          -5.3          -5.4                  -5.3  1.00       127
  141   Shelton Sampson Jr.   UL       WR     WR27        153.8          -5.4           2.3                  -5.4  1.00       101
  142        Cooper Barkate  MIA       WR     WR28        153.6          -5.6           2.1                  -5.6  1.00       103
  143         Darian Mensah  MIA       QB     QB49        218.1         -27.0         -27.1                  -5.9  1.00       241
  144          Aidan Chiles   NU       QB     QB50        217.7         -27.4         -27.5                  -6.3  1.00       243
  145 Carlos Del Rio-Wilson MRSH       QB     QB51        217.5         -27.6         -27.7                  -6.5  1.00       246
  146        Ashton Daniels  FSU       QB     QB52        217.4         -27.7         -27.8                  -6.6  1.00       272
  147          Nathan Hayes NDSU       QB     QB53        216.5         -28.6         -28.7                  -7.5  1.00       259
  148    Isaiah Sategna III   OU       WR     WR29        151.5          -7.7          -2.1                  -7.7  1.00       116
  149          Sawyer Seidl WAKE       RB     RB66        151.4          -7.8          -7.9                  -7.8  1.00       131
  150       Keenan Phillips  USA       RB     RB67        151.3          -7.9          -8.0                  -7.9  0.98       132

## 25 largest risers (better rank)

- Faizon Brandon (QB TENN): 4292 → 245  named-QB prior; QB42 vs starter VORP; proj 58.1→194.5
- Davis Warren (QB STAN): 2868 → 478  named-QB prior; QB42 vs starter VORP; proj 114.1→167.3
- Billy Edwards Jr. (QB UNC): 1820 → 373  named-QB prior; QB42 vs starter VORP; proj 135.3→177.9
- Keelon Russell (QB ALA): 1592 → 343  named-QB prior; QB42 vs starter VORP; proj 142.6→181.6
- Quinn Henicle (QB ODU): 1239 → 289  named-QB prior; QB42 vs starter VORP; proj 155.7→188.1
- Luke Weaver (QB SJSU): 1086 → 265  named-QB prior; QB42 vs starter VORP; proj 161.5→191.0
- Jordon Davison (RB ORE): 574 → 79  managed replacement on 6 missed games
- Tayven Jackson (QB UNT): 555 → 288  QB42 vs starter VORP
- DJ Lagway (QB BAY): 543 → 279  QB42 vs starter VORP
- Jaden Craig (QB TCU): 546 → 282  QB42 vs starter VORP
- Jacurri Brown (QB RICE): 533 → 272  QB42 vs starter VORP
- Rickie Collins (QB KENN): 508 → 263  QB42 vs starter VORP
- Cutter Boley (QB ASU): 493 → 259  QB42 vs starter VORP
- Nico Iamaleava (QB UCLA): 480 → 252  QB42 vs starter VORP
- Bryce Underwood (QB MICH): 478 → 251  QB42 vs starter VORP
- Sam Leavitt (QB LSU): 440 → 232  QB42 vs starter VORP
- Jack Layne (QB UNM): 436 → 231  QB42 vs starter VORP
- Ben Finley (QB AKR): 418 → 222  QB42 vs starter VORP
- Mitch Griffis (QB ECU): 385 → 211  QB42 vs starter VORP
- Roman Gagliano (QB MTSU): 367 → 206  QB42 vs starter VORP
- Dru DeShields (QB KENT): 362 → 204  QB42 vs starter VORP
- Blaze Berlowitz (QB VAN): 358 → 200  QB42 vs starter VORP
- Dante Moore (QB ORE): 354 → 198  QB42 vs starter VORP
- Ethan Vasko (QB LIB): 333 → 192  QB42 vs starter VORP
- Waymond Jordan (RB USC): 260 → 122  proj 128.6→157.9; committee/split scenario

## 25 largest fallers (worse rank)

- Ryan Staub (QB TENN): 1042 → 4308  named-QB backup lock; QB42 vs starter VORP; proj 163.5→50.5
- Jackson Arnold (QB UNLV): 195 → 1440  QB42 vs starter VORP; proj 225.1→112.6; committee/split scenario
- Alex Orji (QB UNLV): 1541 → 2397  QB42 vs starter VORP; proj 144.4→84.9; committee/split scenario
- Chris Corbo (TE GT): 276 → 587  FLEX replacement (no TE baseline)
- Benjamin Brahmer (TE PSU): 224 → 510  FLEX replacement (no TE baseline)
- Bryson Washington (RB AUB): 128 → 414  proj 153.8→108.7; committee/split scenario
- Peter Clarke (TE TEM): 229 → 513  FLEX replacement (no TE baseline)
- Brody Foley (TE LOU): 233 → 515  FLEX replacement (no TE baseline)
- Trey'Dez Green (TE LSU): 186 → 431  FLEX replacement (no TE baseline)
- Terrance Carter Jr. (TE TTU): 170 → 396  FLEX replacement (no TE baseline)
- Garrett Oakley (TE KSU): 157 → 366  FLEX replacement (no TE baseline)
- Dylan Wade (TE UCF): 133 → 322  FLEX replacement (no TE baseline)
- George MacIntyre (QB TENN): 4215 → 4380  named-QB backup lock; QB42 vs starter VORP; proj 87.7→34.8
- Nate Levicki (TE WMU): 115 → 276  FLEX replacement (no TE baseline)
- Kaden Feagin (TE ILL): 33 → 102  FLEX replacement (no TE baseline)
- Junior Sherrill (WR VAN): 88 → 134  lineup-optimizer VORP vs old per-position replacement
- Keshaun Singleton (WR AUB): 87 → 133  lineup-optimizer VORP vs old per-position replacement
- Duce Robinson (WR FSU): 90 → 136  lineup-optimizer VORP vs old per-position replacement
- Jordan Dwyer (WR TCU): 84 → 129  lineup-optimizer VORP vs old per-position replacement
- Nico Brown (WR STAN): 92 → 137  lineup-optimizer VORP vs old per-position replacement
- Ryan Coleman-Williams (WR ALA): 94 → 139  lineup-optimizer VORP vs old per-position replacement
- Josh Dallas (WR GASO): 299 → 344  lineup-optimizer VORP vs old per-position replacement
- Jaden Barnes (WR CLT): 93 → 138  lineup-optimizer VORP vs old per-position replacement
- Hayden Eligon II (WR NU): 293 → 338  lineup-optimizer VORP vs old per-position replacement
- Chauncy Cobb (WR ARST): 295 → 339  lineup-optimizer VORP vs old per-position replacement

## Depth-chart / news audit

- `named_starter_low_probability` Nick Osho: starter_probability=0.7
- `needs_manual_confirmation` Nick Osho: Our board has Osho ahead of White. Confirm official UNT depth; some public boards flip them.
- `needs_manual_confirmation` Thomas Gotkowski: Current M-OH QB1 on this board. Prompt flagged a Miami (OH) QB injury/depth change — not confirmed as of 2026-08-25.
- `unreconciled_lead_roles` Ahmad Hardy, Jamal Roberts: MIZ RB [1.0, 0.98]

## K / D/ST

No kicking or team-defense stats in `fetch.py` (`CATEGORIES` is passing/rushing/receiving/fumbles). Not fabricated. Stream K15 / D/ST15 in the client.

## Unresolved assumptions

- No CFBD dump in this environment, so model.py was not retrained. Tuned board is a post-process of projections_2026.csv.
- Team opportunity budgets (plays/attempts/targets/goal-line) are not reconciled; only 2-player contested rooms get a scenario identity.
- Transfer translation (Nelson, Phillips, Hughes, Brown, Leavitt) is still the v2 ML + from_fcs flag, not a split workload/efficiency/LOC model.
- Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; the TE scarcity bug is fixed, the skill mix is not.
- Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model.
- Role percentiles for non-committee players are a documented residual band, not a weekly Monte Carlo.
- Hardy/Davison availability is a games band around the override, not a week-by-week return tree.
- UNT Osho vs White and Miami (OH) QB depth were not confirmed on official team sites as of 2026-08-25.
- Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.
- No walk-forward backtest in this pass: data/ is not present.
