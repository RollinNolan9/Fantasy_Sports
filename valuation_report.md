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
| scoring_ppr | 0.5 |
| waiver replacement | RB100 = 10.75 PPG (129.0 / 12 games) |
| stash cost | 4.0 pts when missed games ≥ 4 |

## Starter composition

{
  "n_qb": 28,
  "n_skill": 84,
  "n_rb": 55,
  "n_wr": 28,
  "n_te": 1
}

FLEX replacement (first excluded skill): 157.2
WR29 (mandatory-WR replacement): 151.5
QB cutoffs (first player outside N rostered): 28→245.1, 35→228.3, 42→224.0
TE in the 84 skill starters: 1 (optional FLEX only)

Percentile columns p10/p50/p90 are **managed_season_points** (null unless a committee, dual-QB, named-QB-prior, or injury-ramp scenario exists). floor_rank / ceiling_rank rank the full pool using p10/p90, filling unmodeled rows with managed_season_points.

## 28 / 35 / 42 QB sensitivity (top 15 QBs by draft-adjusted value)

 rank                name team  projected_points_if_active  starter_vorp  qb35_adjusted_value  qb42_adjusted_value  draft_adjusted_value
    2         Byrum Brown  AUB                       313.9          68.8                 85.6                 89.9                  89.9
    3      Conner Weigman  HOU                       312.1          67.0                 83.8                 88.1                  88.1
    4        Brad Jackson TXST                       310.0          64.9                 81.7                 86.0                  86.0
   12       Devon Dampier UTAH                       286.4          41.3                 58.1                 62.4                  62.4
   15       Avery Johnson  KSU                       280.3          35.2                 52.0                 56.3                  56.3
   17         Marcel Reed TA&M                       279.9          34.8                 51.6                 55.9                  55.9
   19       Bryson Barnes  USU                       273.4          28.3                 45.1                 49.4                  49.4
   23       Colton Joseph  WIS                       269.6          24.5                 41.3                 45.6                  45.6
   38      Bear Bachmeier  BYU                       260.9          15.8                 32.6                 36.9                  36.9
   41  Trinidad Chambliss MISS                       259.7          14.6                 31.4                 35.7                  35.7
   43      Nick Minicucci  DEL                       257.9          12.8                 29.6                 33.9                  33.9
   44 Demond Williams Jr. WASH                       257.7          12.6                 29.4                 33.7                  33.7
   46         Liam Szarka   AF                       257.2          12.1                 28.9                 33.2                  33.2
   47        Arch Manning  TEX                       256.9          11.8                 28.6                 32.9                  32.9
   49          Broc Lowry  WMU                       255.4          10.3                 27.1                 31.4                  31.4

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

 rank playerId                        name team position pos_rank  proj_points  managed_vorp  starter_vorp  draft_adjusted_value  role  old_rank
    1  5086388                  Kewan Lacy MISS       RB      RB1        252.6          95.4          95.4                  95.4  1.00         1
    2  4880272                 Byrum Brown  AUB       QB      QB1        313.9          68.8          68.8                  89.9  1.00         4
    3  4685574              Conner Weigman  HOU       QB      QB2        312.1          67.0          67.0                  88.1  1.00         5
    4  5148803                Brad Jackson TXST       QB      QB3        310.0          64.9          64.9                  86.0  1.00         9
    5  4918126                   LJ Martin  BYU       RB      RB2        240.4          83.2          83.2                  83.2  1.00         2
    6  4918103                    Cam Cook  WVU       RB      RB3        231.2          74.0          74.0                  74.0  1.00         3
    7  5079574             Jordan Marshall MICH       RB      RB4        225.0          67.8          67.8                  67.8  1.00       114
    8  4921108               DeSean Bishop TENN       RB      RB5        224.2          67.0          67.0                  67.0  1.00         6
    9  5076122                Evan Dickens   BC       RB      RB6        224.1          66.9          66.9                  66.9  1.00         7
   10  5125754              Jai'Den Thomas UNLV       RB      RB7        223.5          66.3          66.3                  66.3  1.00         8
   11  5152414                 Beau Sparks TXST       WR      WR1        214.9          57.7          63.4                  63.4  1.00        10
   12  5105849               Devon Dampier UTAH       QB      QB4        286.4          41.3          41.3                  62.4  1.00        21
   13  5197065                 Ahmad Hardy  MIZ       RB      RB8        194.7          59.0          76.4                  59.0  1.00        14
   14  5209945              Antwan Raymond RUTG       RB      RB9        213.9          56.7          56.7                  56.7  1.00        11
   15  4870857               Avery Johnson  KSU       QB      QB5        280.3          35.2          35.2                  56.3  1.00        35
   16  5223167          Will Henderson III UTSA       RB     RB10        213.4          56.2          56.2                  56.2  1.00        12
   17  4870971                 Marcel Reed TA&M       QB      QB6        279.9          34.8          34.8                  55.9  1.00        36
   18  5079720              Jeremiah Smith  OSU       WR      WR2        207.1          49.9          55.6                  55.6  1.00        13
   19  4695600               Bryson Barnes  USU       QB      QB7        273.4          28.3          28.3                  49.4  1.00        42
   20  5132629              Braylon Staley TENN       WR      WR3        200.5          43.3          49.0                  49.0  1.00        15
   21  5092811                   CJ Miller  TOL       RB     RB11        205.6          48.4          48.4                  48.4  1.00        16
   22  5173431             Wayshawn Parker UTAH       RB     RB12        205.5          48.3          48.3                  48.3  1.00        17
   23  5125715               Colton Joseph  WIS       QB      QB8        269.6          24.5          24.5                  45.6  1.00        48
   24  5258016               Caleb Hawkins OKST       RB     RB13        202.6          45.4          45.4                  45.4  1.00        18
   25  4431328          Rodney Hammond Jr.  SAC       RB     RB14        201.0          43.8          43.8                  43.8  1.00        20
   26  5079580               Mike Matthews TENN       WR      WR4        195.1          37.9          43.6                  43.6  1.00        19
   27  5030333           Sedrick Alexander  VAN       RB     RB15        198.8          41.6          41.6                  41.6  1.00        22
   28  5141423              Jordon Davison  ORE       RB     RB16        198.2          41.0          41.0                  41.0  1.00       574
   29  5079345                Mario Craver TA&M       WR      WR5        192.3          35.1          40.8                  40.8  1.00        23
   30  5079663                Jeremy Payne  TCU       RB     RB17        197.7          40.5          40.5                  40.5  1.00        24
   31  5086034                 Cam Edwards  MSU       RB     RB18        197.0          39.8          39.8                  39.8  1.00        25
   32  5084771                     KJ Duff RUTG       WR      WR6        191.0          33.8          39.5                  39.5  1.00        26
   33  4914830               Easton Messer  FAU       WR      WR7        190.4          33.2          38.9                  38.9  1.00        27
   34  4911971                Jahiem White  UNT       RB     RB19        196.0          38.8          38.8                  38.8  1.00       232
   35  5220197              Fluff Bothwell MSST       RB     RB20        195.6          38.4          38.4                  38.4  1.00        28
   36  5159175               Malachi Toney  MIA       WR      WR8        189.4          32.2          37.9                  37.9  1.00        29
   37  5141517                  Bo Jackson  OSU       RB     RB21        194.8          37.6          37.6                  37.6  1.00        30
   38  5141367              Bear Bachmeier  BYU       QB      QB9        260.9          15.8          15.8                  36.9  1.00        61
   39  5077060                Amare Thomas  HOU       WR      WR9        188.3          31.1          36.8                  36.8  1.00        31
   40  5079742             Aneyas Williams   ND       RB     RB22        193.4          36.2          36.2                  36.2  1.00        32
   41  4911529          Trinidad Chambliss MISS       QB     QB10        259.7          14.6          14.6                  35.7  1.00        62
   42  5164332               Nate Sheppard DUKE       RB     RB23        192.8          35.6          35.6                  35.6  1.00        34
   43  5153846              Nick Minicucci  DEL       QB     QB11        257.9          12.8          12.8                  33.9  1.00        64
   44  5079653         Demond Williams Jr. WASH       QB     QB12        257.7          12.6          12.6                  33.7  1.00        65
   45  5078244              Caleb Komolafe   NU       RB     RB24        190.5          33.3          33.3                  33.3  1.00        37
   46  5238868                 Liam Szarka   AF       QB     QB13        257.2          12.1          12.1                  33.2  1.00        68
   47  4870906                Arch Manning  TEX       QB     QB14        256.9          11.8          11.8                  32.9  1.00        69
   48  5155048           L.J. Phillips Jr. IOWA       RB     RB25        189.2          32.0          32.0                  32.0  0.98        38
   49  5074245                  Broc Lowry  WMU       QB     QB15        255.4          10.3          10.3                  31.4  1.00        73
   50  4685578             Gunner Stockton  UGA       QB     QB16        254.9           9.8           9.8                  30.9  1.00        74
   51  4801717                 Noah Fifita ARIZ       QB     QB17        254.7           9.6           9.6                  30.7  1.00        75
   52  4915980                 John Mateer   OU       QB     QB18        254.4           9.3           9.3                  30.4  1.00        76
   53  5085006               Jalen Buckley  WMU       RB     RB26        186.5          29.3          29.3                  29.3  1.00        40
   54  5114311              Jackson Harris  LSU       WR     WR10        180.3          23.1          28.8                  28.8  0.98        41
   55  5080403               Jaylen Raynor  ISU       QB     QB19        252.5           7.4           7.4                  28.5  1.00        80
   56  5079322                 Jadan Baugh  FLA       RB     RB27        185.5          28.3          28.3                  28.3  1.00        43
   57  4816099                Javen Jacobs  USU       RB     RB28        185.4          28.2          28.2                  28.2  1.00        44
   58  5079369                     CJ Carr   ND       QB     QB20        251.6           6.5           6.5                  27.6  1.00        81
   59  4911929          Alonza Barnett III  UCF       QB     QB21        251.1           6.0           6.0                  27.1  0.98        83
   60  5079349                 Isaac Brown  LOU       RB     RB29        183.5          26.3          26.3                  26.3  1.00        45
   61  5044387           Anthony Colandrea  NEB       QB     QB22        250.0           4.9           4.9                  26.0  1.00        86
   62  5167252                Duncan Brune OHIO       RB     RB30        183.0          25.8          25.8                  25.8  1.00        46
   63  4870513               Maddux Madsen BOIS       QB     QB23        249.4           4.3           4.3                  25.4  1.00        89
   64  4870760              Justice Haynes   GT       RB     RB31        182.4          25.2          25.2                  25.2  1.00        47
   65  4869991              Caden Veltkamp  FAU       QB     QB24        248.9           3.8           3.8                  24.9  1.00        91
   66  4870934             Rueben Owens II TA&M       RB     RB32        181.9          24.7          24.7                  24.7  1.00        50
   67  5084582                 Jordan Gant  AKR       RB     RB33        181.8          24.6          24.6                  24.6  1.00        51
   68  5218633                  Ryan Wingo  TEX       WR     WR11        176.0          18.8          24.5                  24.5  1.00        49
   69  5125823                 DJ McKinney TLSA       RB     RB34        181.5          24.3          24.3                  24.3  0.99        52
   70  4838536                Tyler Hughes  WYO       QB     QB25        247.8           2.7           2.7                  23.8  0.99       100
   71  4912453                Lucky Sutton SDSU       RB     RB35        181.0          23.8          23.8                  23.8  1.00        53
   72  5177084              Kamario Taylor MSST       QB     QB26        247.1           2.0           2.0                  23.1  0.96       104
   73  5079712                Julian Sayin  OSU       QB     QB27        246.8           1.7           1.7                  22.8  1.00       106
   74  5088153                Micahi Danzy  FSU       WR     WR12        173.6          16.4          22.1                  22.1  1.00        54
   75  5154734               Griffin Wilde   NU       WR     WR13        173.0          15.8          21.5                  21.5  1.00        55
   76  5141677            Ja'Kyrian Turner PITT       RB     RB36        178.6          21.4          21.4                  21.4  1.00        56
   77  4685454               Jayden Maiava  USC       QB     QB28        245.2           0.1           0.1                  21.2  1.00       112
   78  5307005              Mason McKenzie   BC       QB     QB29        245.1           0.0          -0.1                  21.1  0.82       113
   79  5122157                 Caden Creel JXST       QB     QB30        244.3          -0.8          -0.9                  20.3  1.00       121
   80  5126468                Will Hammond  TTU       QB     QB31        243.7          -1.4          -1.5                  19.7  0.95       123
   81  5125900                  Joshua Dye MISS       RB     RB37        176.8          19.6          19.6                  19.6  0.92        57
   82  5153885               Rodney Nelson M-OH       RB     RB38        176.1          18.9          18.9                  18.9  0.70        58
   83  4920901               Darius Taylor MINN       RB     RB39        175.4          18.2          18.2                  18.2  1.00        59
   84  5084047                Nate Frazier  UGA       RB     RB40        174.3          17.1          17.1                  17.1  1.00        60
   85  5083042             Skyler Locklear MOST       QB     QB32        238.8          -6.3          -6.4                  14.8  1.00       136
   86  4912342                Wayne Knight UCLA       RB     RB41        171.2          14.0          14.0                  14.0  1.00        63
   87  5150297                Cale Hellums ARMY       QB     QB33        236.7          -8.4          -8.5                  12.7  1.00       142
   88  5077502               Carson Hansen  PSU       RB     RB42        169.9          12.7          12.7                  12.7  1.00        66
   89  5226019               Caden Pinnick  WSU       QB     QB34        236.6          -8.5          -8.6                  12.6  0.97       145
   90  5148787                 Wyatt Young OKST       WR     WR14        163.7           6.5          12.2                  12.2  1.00        67
   91  4871076          Quintrevion Wisner  FSU       RB     RB43        168.5          11.3          11.3                  11.3  1.00        70
   92  5079687                Jordan Shipp  UNC       WR     WR15        162.2           5.0          10.7                  10.7  1.00        71
   93  4870736           Mark Fletcher Jr.  MIA       RB     RB44        167.8          10.6          10.6                  10.6  1.00        72
   94  5084135              Pofele Ashlock  HAW       WR     WR16        160.5           3.3           9.0                   9.0  1.00        77
   95  4918108               Jordan Napier SDSU       WR     WR17        159.5           2.3           8.0                   8.0  1.00        79
   96  5152158             Deuce Alexander MISS       WR     WR18        159.5           2.3           8.0                   8.0  1.00        78
   97  5152815               Danny Scudero COLO       WR     WR19        157.6           0.4           6.1                   6.1  1.00        82
   98  4832804                Jordan Dwyer  TCU       WR     WR20        157.4           0.2           5.9                   5.9  1.00        84
   99  5078144             Landen Chambers  UCF       RB     RB45        163.0           5.8           5.8                   5.8  0.93        85
  100  5121879           Keshaun Singleton  AUB       WR     WR21        156.4          -0.8           4.9                   4.9  1.00        87
  101  5158343             Braxton Woodson NAVY       QB     QB35        228.5         -16.6         -16.7                   4.5  1.00       180
  102  5078165             Junior Sherrill  VAN       WR     WR22        156.0          -1.2           4.5                   4.5  1.00        88
  103  5171031                  Matt Vezza OHIO       QB     QB36        228.3         -16.8         -16.9                   4.3  1.00       181
  104  4870922               Duce Robinson  FSU       WR     WR23        155.7          -1.5           4.2                   4.2  1.00        90
  105  5094032                  Nico Brown STAN       WR     WR24        155.2          -2.0           3.7                   3.7  0.96        92
  106  4870728                Kaden Feagin  ILL       TE      TE1        160.8           3.6           3.6                   3.6  1.00        33
  107  5153730                Jaden Barnes  CLT       WR     WR25        155.1          -2.1           3.6                   3.6  1.00        93
  108  5146725        Kaden Shields-Dutton  FAU       RB     RB46        160.6           3.4           3.4                   3.4  0.98        95
  109  5143191                  Micah Ford STAN       RB     RB47        160.4           3.2           3.2                   3.2  1.00        97
  110  5154284            Ramone Green Jr. MOST       RB     RB48        160.4           3.2           3.2                   3.2  1.00        96
  111  5141711       Ryan Coleman-Williams  ALA       WR     WR26        154.7          -2.5           3.2                   3.2  1.00        94
  112  5219834             Drew Mestemaker OKST       QB     QB37        227.1         -18.0         -18.1                   3.1  1.00       185
  113  4685445                Rayshon Luke FRES       RB     RB49        160.3           3.1           3.1                   3.1  1.00        98
  114  5227209          Anthony Reagan Jr.   UL       RB     RB50        160.3           3.1           3.1                   3.1  0.99        99
  115  4805256                Sutton Smith  ARK       RB     RB51        159.7           2.5           2.5                   2.5  1.00       102
  116  4685696                Beau Pribula  UVA       QB     QB38        226.3         -18.8         -18.9                   2.3  0.96       190
  117  4871010         Shelton Sampson Jr.   UL       WR     WR27        153.8          -3.4           2.3                   2.3  1.00       101
  118  4869582                Cam Barfield  HAW       RB     RB52        159.3           2.1           2.1                   2.1  1.00       105
  119  4804878              Cooper Barkate  MIA       WR     WR28        153.6          -3.6           2.1                   2.1  1.00       103
  120  4689529             Kenji Christian CONN       RB     RB53        159.2           2.0           2.0                   2.0  1.00       107
  121  5159948           Chris Johnson Jr. CLEM       RB     RB54        159.2           2.0           2.0                   2.0  1.00       108
  122  5084769                Angel Flores  CMU       QB     QB39        225.1         -20.0         -20.1                   1.1  1.00       194
  123  5141695            Malik Washington   MD       QB     QB40        224.9         -20.2         -20.3                   0.9  1.00       196
  124  5079506                 Daniel Hill  ALA       RB     RB55        157.7           0.5           0.5                   0.5  1.00       111
  125  4801299                 Rocco Becht  PSU       QB     QB41        224.4         -20.7         -20.8                   0.4  1.00       198
  126  5084084              Kevin Jennings  SMU       QB     QB42        224.2         -20.9         -21.0                   0.2  1.00       199
  127  4795295                Katin Houser  ILL       QB     QB43        224.0         -21.1         -21.2                   0.0  1.00       200
  128  5146724               Turbo Richard   IU       RB     RB56        157.2           0.0          -0.5                   0.0  1.00       118
  129  5080703          Isaiah Sategna III   OU       WR     WR29        151.5          -5.7          -2.1                   0.0  1.00       116
  130  5141586              Dakorien Moore  ORE       WR     WR30        151.2          -6.0          -2.4                  -0.3  1.00       119
  131  5224764                 Sean Wilson  DEL       WR     WR31        151.2          -6.0          -2.4                  -0.3  0.98       117
  132  5193302           Telly Johnson Jr.  NIU       RB     RB57        156.7          -0.5          -1.0                  -0.5  1.00       120
  133  4881032               Taron Dickens  NIU       QB     QB44        223.2         -21.9         -22.0                  -0.8  0.95       205
  134  4907671           Anthony Evans III MSST       WR     WR32        150.3          -6.9          -3.3                  -1.2  1.00       122
  135  4685237               Michael Allen  ECU       RB     RB58        155.8          -1.4          -1.9                  -1.4  0.95       124
  136  5079301                   CJ Bailey NCSU       QB     QB45        222.4         -22.7         -22.8                  -1.6  1.00       209
  137  4869553            Bishop Davenport  USA       QB     QB46        222.2         -22.9         -23.0                  -1.8  1.00       211
  138  5101124               Micah Alejado  HAW       QB     QB47        222.2         -22.9         -23.0                  -1.8  1.00       212
  139  4870642               Jeremiah Cobb  AUB       RB     RB59        155.0          -2.2          -2.7                  -2.2  1.00       456
  140  4871091              Lunch Winfield   UL       QB     QB48        221.7         -23.4         -23.5                  -2.3  1.00       213
  141  5150424               Jordan Faison   ND       WR     WR33        149.1          -8.1          -4.5                  -2.4  1.00       125
  142  5156906                  Bill Davis   VT       RB     RB60        153.9          -3.3          -3.8                  -3.3  1.00       127
  143  5078312               Nyziah Hunter  NEB       WR     WR34        147.9          -9.3          -5.7                  -3.6  1.00       126
  144  5141572                Andrew Marsh MICH       WR     WR35        147.1         -10.1          -6.5                  -4.4  0.99       129
  145  5194795 Na'eem Abdul-Rahim Gladding   MD       WR     WR36        145.9         -11.3          -7.7                  -5.6  0.99       130
  146  5155532                Sawyer Seidl WAKE       RB     RB61        151.4          -5.8          -6.3                  -5.8  1.00       131
  147  5121169               Darian Mensah  MIA       QB     QB49        218.1         -27.0         -27.1                  -5.9  1.00       241
  148  5295070             Keenan Phillips  USA       RB     RB62        151.3          -5.9          -6.4                  -5.9  0.98       132
  149  4717724             Rashod Dubinion  APP       RB     RB63        151.2          -6.0          -6.5                  -6.0  1.00       134
  150  5075805                Aidan Chiles   NU       QB     QB50        217.7         -27.4         -27.5                  -6.3  1.00       243

## 20 largest risers (better rank)

- David McComb (QB M-OH): 4403 → 378  named-QB prior; QB42 vs starter VORP; proj 30.8→181.5
- Faizon Brandon (QB TENN): 4292 → 272  named-QB prior; QB42 vs starter VORP; proj 58.1→194.5
- Davis Warren (QB STAN): 2868 → 539  named-QB prior; QB42 vs starter VORP; proj 114.1→167.3
- Billy Edwards Jr. (QB UNC): 1820 → 417  named-QB prior; QB42 vs starter VORP; proj 135.3→177.9
- Keelon Russell (QB ALA): 1592 → 374  named-QB prior; QB42 vs starter VORP; proj 142.6→181.6
- Quinn Henicle (QB ODU): 1239 → 318  named-QB prior; QB42 vs starter VORP; proj 155.7→188.1
- Luke Weaver (QB SJSU): 1086 → 294  named-QB prior; QB42 vs starter VORP; proj 161.5→191.0
- Jordon Davison (RB ORE): 574 → 28  proj 99.1→198.2
- Jeremiah Cobb (RB AUB): 456 → 139  proj 107.7→155.0
- Jacurri Brown (QB RICE): 533 → 300  QB42 vs starter VORP
- Rickie Collins (QB KENN): 508 → 292  QB42 vs starter VORP
- Cutter Boley (QB ASU): 493 → 286  QB42 vs starter VORP
- Nico Iamaleava (QB UCLA): 480 → 281  QB42 vs starter VORP
- Jahiem White (RB UNT): 232 → 34  proj 131.3→196.0
- Bryce Underwood (QB MICH): 478 → 280  QB42 vs starter VORP
- Sam Leavitt (QB LSU): 440 → 258  QB42 vs starter VORP
- Ben Finley (QB AKR): 418 → 236  QB42 vs starter VORP
- Jack Layne (QB UNM): 436 → 256  QB42 vs starter VORP
- Mitch Griffis (QB ECU): 385 → 225  QB42 vs starter VORP
- Roman Gagliano (QB MTSU): 367 → 217  QB42 vs starter VORP

## 20 largest fallers (worse rank)

- Ryan Staub (QB TENN): 1042 → 4308  named-QB backup lock; QB42 vs starter VORP; proj 163.5→50.5
- Thomas Gotkowski (QB M-OH): 1165 → 4324  named-QB backup lock; QB42 vs starter VORP; proj 158.2→46.0
- Juelz Goff (RB BOIS): 745 → 2839  proj 89.8→15.4
- Quinten Joyner (RB TTU): 815 → 2718  proj 85.7→17.1
- Harry Stewart III (RB BOIS): 1791 → 3294  proj 48.5→11.1
- Jackson Arnold (QB UNLV): 195 → 1554  QB42 vs starter VORP; proj 225.1→112.6; committee/split scenario
- Riley Wormley (RB USC): 2451 → 3563  proj 35.7→8.7
- Alex Orji (QB UNLV): 1541 → 2652  QB42 vs starter VORP; proj 144.4→84.9; committee/split scenario
- King Miller (RB USC): 223 → 943  proj 132.0→75.5; committee/split scenario
- Waymond Jordan (RB USC): 260 → 948  proj 128.6→75.3; committee/split scenario
- Dylan Riley (RB BOIS): 137 → 737  proj 150.8→86.8; committee/split scenario
- Sire Gaines (RB BOIS): 138 → 738  proj 150.8→86.8; committee/split scenario
- Cameron Dickey (RB TTU): 109 → 646  proj 159.0→92.9; committee/split scenario
- J'Koby Williams (RB TTU): 110 → 645  proj 159.0→92.9; committee/split scenario
- Chris Corbo (TE GT): 276 → 634  FLEX replacement (no TE baseline)
- Benjamin Brahmer (TE PSU): 224 → 556  FLEX replacement (no TE baseline)
- Peter Clarke (TE TEM): 229 → 561  FLEX replacement (no TE baseline)
- Brody Foley (TE LOU): 233 → 563  FLEX replacement (no TE baseline)
- Bryson Washington (RB AUB): 128 → 444  proj 153.8→108.7; committee/split scenario
- Trey'Dez Green (TE LSU): 186 → 461  FLEX replacement (no TE baseline)

## Player-level regression diagnostics

Drivers only. Not forced to consensus.

Potentially underprojected:
- Malachi Toney (WR MIA): rank 29→36; pts 189.4→189.4; ppg 15.78; games 12; role 1.00; start_p 1.00; WR29 draft baseline
- Jordan Marshall (RB MICH): rank 114→7; pts 157.5→225.0; ppg 18.75; games 12; role 1.00; start_p 0.90
- Sam Leavitt (QB LSU): rank 440→258; pts 196.3→196.3; ppg 16.36; games 12; role 0.92; start_p 0.92
- Isaiah Sategna III (WR OU): rank 116→129; pts 151.5→151.5; ppg 12.62; games 12; role 1.00; start_p 1.00; WR29 draft baseline
- Keelon Russell (QB ALA): rank 1592→374; pts 142.6→181.6; ppg 15.13; games 12; role 1.00; start_p 1.00; named-QB prior
- David McComb (QB M-OH): rank 4403→378; pts 30.8→181.5; ppg 15.12; games 12; role 1.00; start_p 1.00; named-QB prior
- Makhi Hughes (RB HOU): rank 388→390; pts 113.7→113.7; ppg 9.48; games 12; role 0.93; start_p 0.93
- Raleek Brown (RB TEX): rank 711→669; pts 91.4→91.4; ppg 7.62; games 12; role 0.90; start_p 0.90

Potentially overprojected:
- Nick Osho (RB UNT): rank 39→238; pts 187.6→131.3; ppg 10.94; games 12; role 0.70; start_p 0.25; committee budget split
- Kaden Feagin (TE ILL): rank 33→106; pts 160.8→160.8; ppg 13.40; games 12; role 1.00; start_p 1.00; FLEX replacement (no TE premium)
- L.J. Phillips Jr. (RB IOWA): rank 38→48; pts 189.2→189.2; ppg 15.77; games 12; role 0.98; start_p 0.98
- Cameron Dickey (RB TTU): rank 109→646; pts 159.0→92.9; ppg 7.74; games 12; role 0.41; start_p 0.50; committee budget split
- J'Koby Williams (RB TTU): rank 110→645; pts 159.0→92.9; ppg 7.74; games 12; role 0.41; start_p 0.50; committee budget split
- Braylon Staley (WR TENN): rank 15→20; pts 200.5→200.5; ppg 16.71; games 12; role 1.00; start_p 1.00; WR29 draft baseline
- Mike Matthews (WR TENN): rank 19→26; pts 195.1→195.1; ppg 16.26; games 12; role 1.00; start_p 1.00; WR29 draft baseline
- Ahmad Hardy (RB MIZ): rank 14→13; pts 211.6→194.7; ppg 19.47; games 10; role 1.00; start_p 1.00; injury/ramp + waiver missed-games

## Contested backfield distributions

p10 / p50 / p90 are managed_season_points. A contested back's p75/p90 is the job-winning share of the team RB budget; every other RB on the team is in the remainder.

### TTU (budget=227.1, shares=1.000, P(win)=1.000)

playerId                  name  managed_season_points  expected_opportunity_share  starter_probability       p10  p50        p75        p90
 5086393       J'Koby Williams                   92.9                    0.408954                  0.5 38.139011 92.9 147.642857 147.642857
 5193580        Cameron Dickey                   92.9                    0.408954                  0.5 38.139011 92.9 147.642857 147.642857
 4917949        Quinten Joyner                   17.1                    0.075418                  0.0       NaN  NaN        NaN        NaN
 5290564         Ashton Rowden                    7.8                    0.034437                  0.0       NaN  NaN        NaN        NaN
 5310308        Loic Tshibangu                    7.8                    0.034402                  0.0       NaN  NaN        NaN        NaN
 5196027 Michael Henderson III                    5.7                    0.024900                  0.0       NaN  NaN        NaN        NaN
 5385737      Sawyer Wilkerson                    2.9                    0.012936                  0.0       NaN  NaN        NaN        NaN

### BOIS (budget=215.4, shares=1.000, P(win)=1.000)

playerId              name  managed_season_points  expected_opportunity_share  starter_probability       p10  p50        p75        p90
 5146712       Dylan Riley                   86.8                    0.402920                  0.5 33.572542 86.8 140.028571 140.028571
 5147379       Sire Gaines                   86.8                    0.402920                  0.5 33.572542 86.8 140.028571 140.028571
 5124975        Juelz Goff                   15.4                    0.071386                  0.0       NaN  NaN        NaN        NaN
 5126514 Harry Stewart III                   11.1                    0.051595                  0.0       NaN  NaN        NaN        NaN
 5244754    Keilan Chavies                    6.5                    0.030142                  0.0       NaN  NaN        NaN        NaN
 5274323     Mariyon Sloan                    5.3                    0.024596                  0.0       NaN  NaN        NaN        NaN
 5295045     Zeke Martinez                    3.5                    0.016441                  0.0       NaN  NaN        NaN        NaN

### USC (budget=188.6, shares=1.000, P(win)=1.000)

playerId             name  managed_season_points  expected_opportunity_share  starter_probability       p10  p50        p75        p90
 5233016      King Miller                   75.5                    0.400283                  0.5 28.392408 75.5 122.571429 122.571429
 5295318   Waymond Jordan                   75.3                    0.399166                  0.5 27.971024 75.3 122.571429 122.571429
 5144164    Riley Wormley                    8.7                    0.046233                  0.0       NaN  NaN        NaN        NaN
 5158934     Shahn Alston                    8.7                    0.046373                  0.0       NaN  NaN        NaN        NaN
 5233015    Cian McKelvey                    8.7                    0.046256                  0.0       NaN  NaN        NaN        NaN
 5159076 Deshonne Redeaux                    7.5                    0.039552                  0.0       NaN  NaN        NaN        NaN
 5386510     Kayne Miller                    2.1                    0.010897                  0.0       NaN  NaN        NaN        NaN
 5386511       Tyson Park                    2.1                    0.011241                  0.0       NaN  NaN        NaN        NaN


## Depth-chart / news audit

- `stale_depth` Nick Osho: 21 days since 2026-08-04
- `named_starter_low_probability` Jahiem White: starter_probability=0.8
- `unreconciled_lead_roles` Ahmad Hardy, Jamal Roberts: MIZ RB [1.0, 0.98]

## K / D/ST

No kicking or team-defense stats in `fetch.py` (`CATEGORIES` is passing/rushing/receiving/fumbles). Not fabricated. Stream K15 / D/ST15 in the client.

## Unresolved assumptions

- No CFBD dump in this environment, so model.py was not retrained. Tuned board is a post-process of projections_2026.csv.
- Team play/target/TD budgets are still not in the ML; only contested RB rooms share one backfield budget.
- Transfer translation (Nelson, Phillips, Hughes, Brown, Leavitt) is still the v2 ML + from_fcs flag.
- Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; only TE scarcity and FLEX replacement changed.
- Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model.
- Percentiles p10/p50/p90 are managed_season_points when a scenario exists; otherwise they stay null. floor_rank/ceiling_rank still cover the full pool.
- Hardy uses a 2-game 60% ramp plus an 8/10/11-game return band, not a medical week tree.
- Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.
- No walk-forward backtest in this pass: data/ is not present.
- Tennessee WR stack (Staley/Matthews) still comes from independent ML rows, not one team passing forecast.
