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
| waiver replacement | RB100 = 10.80 PPG (129.6 / 12 games) |
| stash cost | 4.0 pts when missed games ≥ 4 |

## Starter composition

{
  "n_qb": 28,
  "n_skill": 84,
  "n_rb": 55,
  "n_wr": 28,
  "n_te": 1
}

FLEX replacement (first excluded skill): 157.7
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
   14       Avery Johnson  KSU                       280.3          35.2                 52.0                 56.3                  56.3
   16         Marcel Reed TA&M                       279.9          34.8                 51.6                 55.9                  55.9
   19       Bryson Barnes  USU                       273.4          28.3                 45.1                 49.4                  49.4
   23       Colton Joseph  WIS                       269.6          24.5                 41.3                 45.6                  45.6
   39      Bear Bachmeier  BYU                       260.9          15.8                 32.6                 36.9                  36.9
   41  Trinidad Chambliss MISS                       259.7          14.6                 31.4                 35.7                  35.7
   44      Nick Minicucci  DEL                       257.9          12.8                 29.6                 33.9                  33.9
   45 Demond Williams Jr. WASH                       257.7          12.6                 29.4                 33.7                  33.7
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
    1  5086388                  Kewan Lacy MISS       RB      RB1        252.6          94.9          94.9                  94.9  1.00         1
    2  4880272                 Byrum Brown  AUB       QB      QB1        313.9          68.8          68.8                  89.9  1.00         4
    3  4685574              Conner Weigman  HOU       QB      QB2        312.1          67.0          67.0                  88.1  1.00         5
    4  5148803                Brad Jackson TXST       QB      QB3        310.0          64.9          64.9                  86.0  1.00         9
    5  4918126                   LJ Martin  BYU       RB      RB2        240.4          82.7          82.7                  82.7  1.00         2
    6  4918103                    Cam Cook  WVU       RB      RB3        231.2          73.5          73.5                  73.5  1.00         3
    7  5079574             Jordan Marshall MICH       RB      RB4        225.0          67.3          67.3                  67.3  1.00       114
    8  4921108               DeSean Bishop TENN       RB      RB5        224.2          66.5          66.5                  66.5  1.00         6
    9  5076122                Evan Dickens   BC       RB      RB6        224.1          66.4          66.4                  66.4  1.00         7
   10  5125754              Jai'Den Thomas UNLV       RB      RB7        223.5          65.8          65.8                  65.8  1.00         8
   11  5152414                 Beau Sparks TXST       WR      WR1        214.9          57.2          63.4                  63.4  1.00        10
   12  5105849               Devon Dampier UTAH       QB      QB4        286.4          41.3          41.3                  62.4  1.00        21
   13  5197065                 Ahmad Hardy  MIZ       RB      RB8        194.7          58.6          75.9                  58.6  1.00        14
   14  4870857               Avery Johnson  KSU       QB      QB5        280.3          35.2          35.2                  56.3  1.00        35
   15  5209945              Antwan Raymond RUTG       RB      RB9        213.9          56.2          56.2                  56.2  1.00        11
   16  4870971                 Marcel Reed TA&M       QB      QB6        279.9          34.8          34.8                  55.9  1.00        36
   17  5223167          Will Henderson III UTSA       RB     RB10        213.4          55.7          55.7                  55.7  1.00        12
   18  5079720              Jeremiah Smith  OSU       WR      WR2        207.1          49.4          55.6                  55.6  1.00        13
   19  4695600               Bryson Barnes  USU       QB      QB7        273.4          28.3          28.3                  49.4  1.00        42
   20  5132629              Braylon Staley TENN       WR      WR3        200.5          42.8          49.0                  49.0  1.00        15
   21  5092811                   CJ Miller  TOL       RB     RB11        205.6          47.9          47.9                  47.9  1.00        16
   22  5173431             Wayshawn Parker UTAH       RB     RB12        205.5          47.8          47.8                  47.8  1.00        17
   23  5125715               Colton Joseph  WIS       QB      QB8        269.6          24.5          24.5                  45.6  1.00        48
   24  5258016               Caleb Hawkins OKST       RB     RB13        202.6          44.9          44.9                  44.9  1.00        18
   25  5079580               Mike Matthews TENN       WR      WR4        195.1          37.4          43.6                  43.6  1.00        19
   26  4431328          Rodney Hammond Jr.  SAC       RB     RB14        201.0          43.3          43.3                  43.3  1.00        20
   27  5193580              Cameron Dickey  TTU       RB     RB15        200.9          43.2          43.2                  43.2  0.44       109
   28  5030333           Sedrick Alexander  VAN       RB     RB16        198.8          41.1          41.1                  41.1  1.00        22
   29  5079345                Mario Craver TA&M       WR      WR5        192.3          34.6          40.8                  40.8  1.00        23
   30  5141423              Jordon Davison  ORE       RB     RB17        198.2          40.5          40.5                  40.5  1.00       574
   31  5079663                Jeremy Payne  TCU       RB     RB18        197.7          40.0          40.0                  40.0  1.00        24
   32  5084771                     KJ Duff RUTG       WR      WR6        191.0          33.3          39.5                  39.5  1.00        26
   33  5086034                 Cam Edwards  MSU       RB     RB19        197.0          39.3          39.3                  39.3  1.00        25
   34  4914830               Easton Messer  FAU       WR      WR7        190.4          32.7          38.9                  38.9  1.00        27
   35  4911971                Jahiem White  UNT       RB     RB20        196.0          38.3          38.3                  38.3  1.00       232
   36  5220197              Fluff Bothwell MSST       RB     RB21        195.6          37.9          37.9                  37.9  1.00        28
   37  5159175               Malachi Toney  MIA       WR      WR8        189.4          31.7          37.9                  37.9  1.00        29
   38  5141517                  Bo Jackson  OSU       RB     RB22        194.8          37.1          37.1                  37.1  1.00        30
   39  5141367              Bear Bachmeier  BYU       QB      QB9        260.9          15.8          15.8                  36.9  1.00        61
   40  5077060                Amare Thomas  HOU       WR      WR9        188.3          30.6          36.8                  36.8  1.00        31
   41  4911529          Trinidad Chambliss MISS       QB     QB10        259.7          14.6          14.6                  35.7  1.00        62
   42  5079742             Aneyas Williams   ND       RB     RB23        193.4          35.7          35.7                  35.7  1.00        32
   43  5164332               Nate Sheppard DUKE       RB     RB24        192.8          35.1          35.1                  35.1  1.00        34
   44  5153846              Nick Minicucci  DEL       QB     QB11        257.9          12.8          12.8                  33.9  1.00        64
   45  5079653         Demond Williams Jr. WASH       QB     QB12        257.7          12.6          12.6                  33.7  1.00        65
   46  5238868                 Liam Szarka   AF       QB     QB13        257.2          12.1          12.1                  33.2  1.00        68
   47  4870906                Arch Manning  TEX       QB     QB14        256.9          11.8          11.8                  32.9  1.00        69
   48  5078244              Caleb Komolafe   NU       RB     RB25        190.5          32.8          32.8                  32.8  1.00        37
   49  5074245                  Broc Lowry  WMU       QB     QB15        255.4          10.3          10.3                  31.4  1.00        73
   50  4685578             Gunner Stockton  UGA       QB     QB16        254.9           9.8           9.8                  30.9  1.00        74
   51  4801717                 Noah Fifita ARIZ       QB     QB17        254.7           9.6           9.6                  30.7  1.00        75
   52  4915980                 John Mateer   OU       QB     QB18        254.4           9.3           9.3                  30.4  1.00        76
   53  5085006               Jalen Buckley  WMU       RB     RB26        186.5          28.8          28.8                  28.8  1.00        40
   54  5114311              Jackson Harris  LSU       WR     WR10        180.3          22.6          28.8                  28.8  0.98        41
   55  5080403               Jaylen Raynor  ISU       QB     QB19        252.5           7.4           7.4                  28.5  1.00        80
   56  5079322                 Jadan Baugh  FLA       RB     RB27        185.5          27.8          27.8                  27.8  1.00        43
   57  4816099                Javen Jacobs  USU       RB     RB28        185.4          27.7          27.7                  27.7  1.00        44
   58  5079369                     CJ Carr   ND       QB     QB20        251.6           6.5           6.5                  27.6  1.00        81
   59  4911929          Alonza Barnett III  UCF       QB     QB21        251.1           6.0           6.0                  27.1  0.98        83
   60  5044387           Anthony Colandrea  NEB       QB     QB22        250.0           4.9           4.9                  26.0  1.00        86
   61  5079349                 Isaac Brown  LOU       RB     RB29        183.5          25.8          25.8                  25.8  1.00        45
   62  4870513               Maddux Madsen BOIS       QB     QB23        249.4           4.3           4.3                  25.4  1.00        89
   63  5167252                Duncan Brune OHIO       RB     RB30        183.0          25.3          25.3                  25.3  1.00        46
   64  4869991              Caden Veltkamp  FAU       QB     QB24        248.9           3.8           3.8                  24.9  1.00        91
   65  4870760              Justice Haynes   GT       RB     RB31        182.4          24.7          24.7                  24.7  1.00        47
   66  5218633                  Ryan Wingo  TEX       WR     WR11        176.0          18.3          24.5                  24.5  1.00        49
   67  4870934             Rueben Owens II TA&M       RB     RB32        181.9          24.2          24.2                  24.2  1.00        50
   68  5084582                 Jordan Gant  AKR       RB     RB33        181.8          24.1          24.1                  24.1  1.00        51
   69  4838536                Tyler Hughes  WYO       QB     QB25        247.8           2.7           2.7                  23.8  0.99       100
   70  5125823                 DJ McKinney TLSA       RB     RB34        181.5          23.8          23.8                  23.8  0.99        52
   71  4912453                Lucky Sutton SDSU       RB     RB35        181.0          23.3          23.3                  23.3  1.00        53
   72  5177084              Kamario Taylor MSST       QB     QB26        247.1           2.0           2.0                  23.1  0.96       104
   73  5079712                Julian Sayin  OSU       QB     QB27        246.8           1.7           1.7                  22.8  1.00       106
   74  5088153                Micahi Danzy  FSU       WR     WR12        173.6          15.9          22.1                  22.1  1.00        54
   75  5154734               Griffin Wilde   NU       WR     WR13        173.0          15.3          21.5                  21.5  1.00        55
   76  4685454               Jayden Maiava  USC       QB     QB28        245.2           0.1           0.1                  21.2  1.00       112
   77  5307005              Mason McKenzie   BC       QB     QB29        245.1           0.0          -0.1                  21.1  0.82       113
   78  5141677            Ja'Kyrian Turner PITT       RB     RB36        178.6          20.9          20.9                  20.9  1.00        56
   79  5122157                 Caden Creel JXST       QB     QB30        244.3          -0.8          -0.9                  20.3  1.00       121
   80  5126468                Will Hammond  TTU       QB     QB31        243.7          -1.4          -1.5                  19.7  0.95       123
   81  5125900                  Joshua Dye MISS       RB     RB37        176.8          19.1          19.1                  19.1  0.92        57
   82  5153885               Rodney Nelson M-OH       RB     RB38        176.1          18.4          18.4                  18.4  0.70        58
   83  4920901               Darius Taylor MINN       RB     RB39        175.4          17.7          17.7                  17.7  1.00        59
   84  5084047                Nate Frazier  UGA       RB     RB40        174.3          16.6          16.6                  16.6  1.00        60
   85  5083042             Skyler Locklear MOST       QB     QB32        238.8          -6.3          -6.4                  14.8  1.00       136
   86  4912342                Wayne Knight UCLA       RB     RB41        171.2          13.5          13.5                  13.5  1.00        63
   87  5150297                Cale Hellums ARMY       QB     QB33        236.7          -8.4          -8.5                  12.7  1.00       142
   88  5226019               Caden Pinnick  WSU       QB     QB34        236.6          -8.5          -8.6                  12.6  0.97       145
   89  5077502               Carson Hansen  PSU       RB     RB42        169.9          12.2          12.2                  12.2  1.00        66
   90  5148787                 Wyatt Young OKST       WR     WR14        163.7           6.0          12.2                  12.2  1.00        67
   91  4871076          Quintrevion Wisner  FSU       RB     RB43        168.5          10.8          10.8                  10.8  1.00        70
   92  5079687                Jordan Shipp  UNC       WR     WR15        162.2           4.5          10.7                  10.7  1.00        71
   93  4870736           Mark Fletcher Jr.  MIA       RB     RB44        167.8          10.1          10.1                  10.1  1.00        72
   94  5084135              Pofele Ashlock  HAW       WR     WR16        160.5           2.8           9.0                   9.0  1.00        77
   95  4918108               Jordan Napier SDSU       WR     WR17        159.5           1.8           8.0                   8.0  1.00        79
   96  5152158             Deuce Alexander MISS       WR     WR18        159.5           1.8           8.0                   8.0  1.00        78
   97  5146712                 Dylan Riley BOIS       RB     RB45        165.6           7.9           7.9                   7.9  0.53       137
   98  5152815               Danny Scudero COLO       WR     WR19        157.6          -0.1           6.1                   6.1  1.00        82
   99  4832804                Jordan Dwyer  TCU       WR     WR20        157.4          -0.3           5.9                   5.9  1.00        84
  100  5078144             Landen Chambers  UCF       RB     RB46        163.0           5.3           5.3                   5.3  0.93        85
  101  5121879           Keshaun Singleton  AUB       WR     WR21        156.4          -1.3           4.9                   4.9  1.00        87
  102  5158343             Braxton Woodson NAVY       QB     QB35        228.5         -16.6         -16.7                   4.5  1.00       180
  103  5078165             Junior Sherrill  VAN       WR     WR22        156.0          -1.7           4.5                   4.5  1.00        88
  104  5171031                  Matt Vezza OHIO       QB     QB36        228.3         -16.8         -16.9                   4.3  1.00       181
  105  4870922               Duce Robinson  FSU       WR     WR23        155.7          -2.0           4.2                   4.2  1.00        90
  106  5094032                  Nico Brown STAN       WR     WR24        155.2          -2.5           3.7                   3.7  0.96        92
  107  5153730                Jaden Barnes  CLT       WR     WR25        155.1          -2.6           3.6                   3.6  1.00        93
  108  5141711       Ryan Coleman-Williams  ALA       WR     WR26        154.7          -3.0           3.2                   3.2  1.00        94
  109  5219834             Drew Mestemaker OKST       QB     QB37        227.1         -18.0         -18.1                   3.1  1.00       185
  110  4870728                Kaden Feagin  ILL       TE      TE1        160.8           3.1           3.1                   3.1  1.00        33
  111  5146725        Kaden Shields-Dutton  FAU       RB     RB47        160.6           2.9           2.9                   2.9  0.98        95
  112  5143191                  Micah Ford STAN       RB     RB48        160.4           2.7           2.7                   2.7  1.00        97
  113  5154284            Ramone Green Jr. MOST       RB     RB49        160.4           2.7           2.7                   2.7  1.00        96
  114  4685445                Rayshon Luke FRES       RB     RB50        160.3           2.6           2.6                   2.6  1.00        98
  115  5227209          Anthony Reagan Jr.   UL       RB     RB51        160.3           2.6           2.6                   2.6  0.99        99
  116  4685696                Beau Pribula  UVA       QB     QB38        226.3         -18.8         -18.9                   2.3  0.96       190
  117  4871010         Shelton Sampson Jr.   UL       WR     WR27        153.8          -3.9           2.3                   2.3  1.00       101
  118  4804878              Cooper Barkate  MIA       WR     WR28        153.6          -4.1           2.1                   2.1  1.00       103
  119  4805256                Sutton Smith  ARK       RB     RB52        159.7           2.0           2.0                   2.0  1.00       102
  120  4869582                Cam Barfield  HAW       RB     RB53        159.3           1.6           1.6                   1.6  1.00       105
  121  4689529             Kenji Christian CONN       RB     RB54        159.2           1.5           1.5                   1.5  1.00       107
  122  5159948           Chris Johnson Jr. CLEM       RB     RB55        159.2           1.5           1.5                   1.5  1.00       108
  123  5084769                Angel Flores  CMU       QB     QB39        225.1         -20.0         -20.1                   1.1  1.00       194
  124  5141695            Malik Washington   MD       QB     QB40        224.9         -20.2         -20.3                   0.9  1.00       196
  125  4801299                 Rocco Becht  PSU       QB     QB41        224.4         -20.7         -20.8                   0.4  1.00       198
  126  5084084              Kevin Jennings  SMU       QB     QB42        224.2         -20.9         -21.0                   0.2  1.00       199
  127  4795295                Katin Houser  ILL       QB     QB43        224.0         -21.1         -21.2                   0.0  1.00       200
  128  5079506                 Daniel Hill  ALA       RB     RB56        157.7           0.0          -1.5                   0.0  1.00       111
  129  5080703          Isaiah Sategna III   OU       WR     WR29        151.5          -6.2          -2.1                   0.0  1.00       116
  130  5141586              Dakorien Moore  ORE       WR     WR30        151.2          -6.5          -2.4                  -0.3  1.00       119
  131  5224764                 Sean Wilson  DEL       WR     WR31        151.2          -6.5          -2.4                  -0.3  0.98       117
  132  5146724               Turbo Richard   IU       RB     RB57        157.2          -0.5          -2.0                  -0.5  1.00       118
  133  4881032               Taron Dickens  NIU       QB     QB44        223.2         -21.9         -22.0                  -0.8  0.95       205
  134  5193302           Telly Johnson Jr.  NIU       RB     RB58        156.7          -1.0          -2.5                  -1.0  1.00       120
  135  4907671           Anthony Evans III MSST       WR     WR32        150.3          -7.4          -3.3                  -1.2  1.00       122
  136  5079301                   CJ Bailey NCSU       QB     QB45        222.4         -22.7         -22.8                  -1.6  1.00       209
  137  4869553            Bishop Davenport  USA       QB     QB46        222.2         -22.9         -23.0                  -1.8  1.00       211
  138  5101124               Micah Alejado  HAW       QB     QB47        222.2         -22.9         -23.0                  -1.8  1.00       212
  139  4685237               Michael Allen  ECU       RB     RB59        155.8          -1.9          -3.4                  -1.9  0.95       124
  140  4871091              Lunch Winfield   UL       QB     QB48        221.7         -23.4         -23.5                  -2.3  1.00       213
  141  5150424               Jordan Faison   ND       WR     WR33        149.1          -8.6          -4.5                  -2.4  1.00       125
  142  4870642               Jeremiah Cobb  AUB       RB     RB60        155.0          -2.7          -4.2                  -2.7  1.00       456
  143  5078312               Nyziah Hunter  NEB       WR     WR34        147.9          -9.8          -5.7                  -3.6  1.00       126
  144  5156906                  Bill Davis   VT       RB     RB61        153.9          -3.8          -5.3                  -3.8  1.00       127
  145  5141572                Andrew Marsh MICH       WR     WR35        147.1         -10.6          -6.5                  -4.4  0.99       129
  146  5194795 Na'eem Abdul-Rahim Gladding   MD       WR     WR36        145.9         -11.8          -7.7                  -5.6  0.99       130
  147  5121169               Darian Mensah  MIA       QB     QB49        218.1         -27.0         -27.1                  -5.9  1.00       241
  148  5075805                Aidan Chiles   NU       QB     QB50        217.7         -27.4         -27.5                  -6.3  1.00       243
  149  5155532                Sawyer Seidl WAKE       RB     RB62        151.4          -6.3          -7.8                  -6.3  1.00       131
  150  5084409            Jared Richardson DUKE       WR     WR37        145.2         -12.5          -8.4                  -6.3  0.96       135

## 20 largest risers (better rank)

- David McComb (QB M-OH): 4403 → 380  named-QB prior; QB42 vs starter VORP; proj 30.8→181.5
- Faizon Brandon (QB TENN): 4292 → 271  named-QB prior; QB42 vs starter VORP; proj 58.1→194.5
- Davis Warren (QB STAN): 2868 → 541  named-QB prior; QB42 vs starter VORP; proj 114.1→167.3
- Billy Edwards Jr. (QB UNC): 1820 → 417  named-QB prior; QB42 vs starter VORP; proj 135.3→177.9
- Keelon Russell (QB ALA): 1592 → 376  named-QB prior; QB42 vs starter VORP; proj 142.6→181.6
- Quinn Henicle (QB ODU): 1239 → 320  named-QB prior; QB42 vs starter VORP; proj 155.7→188.1
- Luke Weaver (QB SJSU): 1086 → 296  named-QB prior; QB42 vs starter VORP; proj 161.5→191.0
- Jordon Davison (RB ORE): 574 → 30  proj 99.1→198.2
- Jeremiah Cobb (RB AUB): 456 → 142  proj 107.7→155.0
- Jacurri Brown (QB RICE): 533 → 300  QB42 vs starter VORP
- Rickie Collins (QB KENN): 508 → 293  QB42 vs starter VORP
- Cutter Boley (QB ASU): 493 → 287  QB42 vs starter VORP
- Jahiem White (RB UNT): 232 → 35  proj 131.3→196.0
- Bryce Underwood (QB MICH): 478 → 281  QB42 vs starter VORP
- Nico Iamaleava (QB UCLA): 480 → 283  QB42 vs starter VORP
- Sam Leavitt (QB LSU): 440 → 255  QB42 vs starter VORP
- Jack Layne (QB UNM): 436 → 253  QB42 vs starter VORP
- Ben Finley (QB AKR): 418 → 237  QB42 vs starter VORP
- Mitch Griffis (QB ECU): 385 → 227  QB42 vs starter VORP
- Roman Gagliano (QB MTSU): 367 → 217  QB42 vs starter VORP

## 20 largest fallers (worse rank)

- Ryan Staub (QB TENN): 1042 → 4308  named-QB backup lock; QB42 vs starter VORP; proj 163.5→50.5
- Thomas Gotkowski (QB M-OH): 1165 → 4324  named-QB backup lock; QB42 vs starter VORP; proj 158.2→46.0
- Xavier Williams (RB IOWA): 1070 → 4126  proj 74.7→2.3
- Harry Stewart III (RB BOIS): 1791 → 4116  proj 48.5→2.5
- Brevin Doll (RB IOWA): 2128 → 4172  proj 40.4→1.3
- Nathan McNeil (RB IOWA): 2208 → 4191  proj 39.1→0.9
- Shahn Alston (RB USC): 2812 → 4236  proj 28.3→0.0
- Cian McKelvey (RB USC): 2866 → 4252  proj 26.5→0.0
- Deshonne Redeaux (RB USC): 2860 → 4237  proj 26.6→0.0
- Jackson Arnold (QB UNLV): 195 → 1547  QB42 vs starter VORP; proj 225.1→112.6; committee/split scenario
- O'Lontae Dean (RB IOWA): 3007 → 4213  proj 22.2→0.5
- Juelz Goff (RB BOIS): 745 → 1873  proj 89.8→35.9
- Alex Orji (QB UNLV): 1541 → 2637  QB42 vs starter VORP; proj 144.4→84.9; committee/split scenario
- Kamari Moulton (RB IOWA): 222 → 1102  proj 132.4→66.7; committee/split scenario
- L.J. Phillips Jr. (RB IOWA): 38 → 897  proj 189.2→78.0; committee/split scenario
- Quinten Joyner (RB TTU): 815 → 1669  proj 85.7→42.1
- King Miller (RB USC): 223 → 988  proj 132.0→73.1; committee/split scenario
- Riley Wormley (RB USC): 2451 → 3109  proj 35.7→12.9
- Sire Gaines (RB BOIS): 138 → 580  proj 150.8→98.3; committee/split scenario
- Chris Corbo (TE GT): 276 → 644  FLEX replacement (no TE baseline)

## Player-level regression diagnostics

Drivers only. Not forced to consensus.

Potentially underprojected:
- Malachi Toney (WR MIA): rank 29→37; pts 189.4→189.4; ppg 15.78; games 12; role 1.00; start_p nan; WR29 draft baseline
- Jordan Marshall (RB MICH): rank 114→7; pts 157.5→225.0; ppg 18.75; games 12; role 1.00; start_p 0.90
- Sam Leavitt (QB LSU): rank 440→255; pts 196.3→196.3; ppg 16.36; games 12; role 0.92; start_p nan
- Isaiah Sategna III (WR OU): rank 116→129; pts 151.5→151.5; ppg 12.62; games 12; role 1.00; start_p nan; WR29 draft baseline
- Keelon Russell (QB ALA): rank 1592→376; pts 142.6→181.6; ppg 15.13; games 12; role 1.00; start_p 1.00; named-QB prior
- David McComb (QB M-OH): rank 4403→380; pts 30.8→181.5; ppg 15.12; games 12; role 1.00; start_p 1.00; named-QB prior
- Makhi Hughes (RB HOU): rank 388→397; pts 113.7→113.7; ppg 9.48; games 12; role 0.93; start_p nan
- Raleek Brown (RB TEX): rank 711→674; pts 91.4→91.4; ppg 7.62; games 12; role 0.90; start_p nan

Potentially overprojected:
- Nick Osho (RB UNT): rank 39→244; pts 187.6→131.3; ppg 10.94; games 12; role 0.70; start_p 0.25; committee budget split
- Kaden Feagin (TE ILL): rank 33→110; pts 160.8→160.8; ppg 13.40; games 12; role 1.00; start_p 1.00; FLEX replacement (no TE premium)
- L.J. Phillips Jr. (RB IOWA): rank 38→897; pts 189.2→78.0; ppg 6.50; games 12; role 0.46; start_p 0.45; committee budget split
- Cameron Dickey (RB TTU): rank 109→27; pts 159.0→200.9; ppg 16.74; games 12; role 0.44; start_p 0.50; committee budget split
- J'Koby Williams (RB TTU): rank 110→276; pts 159.0→127.6; ppg 10.63; games 12; role 0.40; start_p 0.33; committee budget split
- Braylon Staley (WR TENN): rank 15→20; pts 200.5→200.5; ppg 16.71; games 12; role 1.00; start_p nan; WR29 draft baseline
- Mike Matthews (WR TENN): rank 19→25; pts 195.1→195.1; ppg 16.26; games 12; role 1.00; start_p nan; WR29 draft baseline
- Ahmad Hardy (RB MIZ): rank 14→13; pts 211.6→194.7; ppg 19.47; games 10; role 1.00; start_p 1.00; injury/ramp + waiver missed-games

## Contested backfield distributions

p10 / p50 / p90 are managed_season_points. Rush follows mutually exclusive winner scenarios; receiving stays player-specific. Every RB on the team is in the remainder.

### TTU (budget=372.3, shares=1.000, P(win)=1.000)

playerId                  name  managed_season_points  expected_opportunity_share  starter_probability        p10   p50       p75       p90
 5193580        Cameron Dickey                  200.9                    0.444752                 0.50 141.290955 200.9 259.53652 259.53652
 5086393       J'Koby Williams                  127.6                    0.403515                 0.33  87.670560 127.6 207.38266 207.38266
 4917949        Quinten Joyner                   42.1                    0.140260                 0.17  21.929707  42.1 138.85208 138.85208
 5290564         Ashton Rowden                    0.7                    0.003855                 0.00        NaN   NaN       NaN       NaN
 5310308        Loic Tshibangu                    0.7                    0.003850                 0.00        NaN   NaN       NaN       NaN
 5196027 Michael Henderson III                    0.3                    0.002572                 0.00        NaN   NaN       NaN       NaN
 5385737      Sawyer Wilkerson                    0.1                    0.001196                 0.00        NaN   NaN       NaN       NaN

### BOIS (budget=304.0, shares=1.000, P(win)=1.000)

playerId              name  managed_season_points  expected_opportunity_share  starter_probability        p10   p50        p75        p90
 5146712       Dylan Riley                  165.6                    0.534876                 0.50 105.795080 165.6 220.220434 220.220434
 5147379       Sire Gaines                   98.3                    0.301823                 0.35  51.720308  98.3 170.541736 170.541736
 5124975        Juelz Goff                   35.9                    0.132541                 0.15  16.136306  35.9 142.673127 142.673127
 5126514 Harry Stewart III                    2.5                    0.015303                 0.00        NaN   NaN        NaN        NaN
 5244754    Keilan Chavies                    0.9                    0.007004                 0.00        NaN   NaN        NaN        NaN
 5274323     Mariyon Sloan                    0.6                    0.005307                 0.00        NaN   NaN        NaN        NaN
 5295045     Zeke Martinez                    0.3                    0.003146                 0.00        NaN   NaN        NaN        NaN

### USC (budget=223.2, shares=1.000, P(win)=1.000)

playerId             name  managed_season_points  expected_opportunity_share  starter_probability       p10   p50        p75        p90
 5295318   Waymond Jordan                  137.2                6.967657e-01                 0.58 90.621675 137.2 167.959445 167.959445
 5233016      King Miller                   73.1                1.883120e-01                 0.32 41.470208  73.1 127.452512 127.452512
 5144164    Riley Wormley                   12.9                1.149206e-01                 0.10  5.125760  12.9  73.794552  73.794552
 5158934     Shahn Alston                    0.0                5.064455e-07                 0.00       NaN   NaN        NaN        NaN
 5159076 Deshonne Redeaux                    0.0                4.319967e-07                 0.00       NaN   NaN        NaN        NaN
 5233015    Cian McKelvey                    0.0                5.051626e-07                 0.00       NaN   NaN        NaN        NaN
 5386510     Kayne Miller                    0.0                1.192651e-07                 0.00       NaN   NaN        NaN        NaN
 5386511       Tyson Park                    0.0                1.230207e-07                 0.00       NaN   NaN        NaN        NaN


## RB-room validation

Scoring, replacement levels, and valuation formulas were not changed (scoring_ppr=0.5, WR29=151.5, FLEX=157.7, QB28/35/42=245.1/228.3/224.0).

`starter_probability` is P(win the RB job) in modeled rooms (sums to 1.0) or a sourced named-starter probability. It is blank when no probability model ran. `role` remains the role score.

### Team RB point pool and share sum

| team | before pool | after pool | before share sum | after share sum | after P(win) |
|---|---:|---:|---:|---:|---:|
| BOIS | 215.4 | 304.0 | 1.000 | 1.000 | 1.000 |
| IOWA | 503.7 | 150.1 | 4.710 | 1.000 | 1.000 |
| TTU | 227.1 | 372.3 | 0.999 | 1.000 | 1.000 |
| USC | 188.6 | 223.2 | 0.999 | 1.000 | 1.000 |

### Top-112 / top-126 positional composition

| cut | when | QB | RB | WR | TE |
|---|---|---:|---:|---:|---:|
| top 112 | before | 37 | 48 | 26 | 1 |
| top 112 | after | 37 | 48 | 26 | 1 |
| top 126 | before | 42 | 55 | 28 | 1 |
| top 126 | after | 42 | 55 | 28 | 1 |

### Players entering top 150

- Cameron Dickey (RB TTU) rank 27
- Dylan Riley (RB BOIS) rank 97
- Jared Richardson (WR DUKE) rank 150

### Players leaving top 150

- L.J. Phillips Jr. (RB IOWA) was rank 48
- Keenan Phillips (RB USA) was rank 148
- Rashod Dubinion (RB APP) was rank 149

### Manually changed role priors (source URL + as-of)

| player | team | P(win) | workload | as-of | source |
|---|---|---:|---:|---|---|
| Cameron Dickey | TTU | 0.50 | 0.47 | 2026-07-30 | https://redraiderswire.usatoday.com/story/sports/college/red-raiders/football/2026/07/30/texas-tech-football-running-backs-preview-2026/91096409007/ |
| J'Koby Williams | TTU | 0.33 | 0.33 | 2026-07-03 | https://www.lubbockonline.com/story/sports/college/red-raiders/2026/07/03/texas-tech-football-jkoby-williams-cameron-dickey-quinten-joyner-joey-mcguire-garret-mcguire/90702732007/ |
| Quinten Joyner | TTU | 0.17 | 0.17 | 2026-07-30 | https://redraiderswire.usatoday.com/story/sports/college/red-raiders/football/2026/07/30/texas-tech-football-running-backs-preview-2026/91096409007/ |
| Dylan Riley | BOIS | 0.50 | 0.48 | 2026-08-15 | https://www.si.com/college/boise-state/football/projecting-boise-state-depth-chart-for-week-1-of-2026-college-football-season |
| Sire Gaines | BOIS | 0.35 | 0.34 | 2026-03-20 | https://www.idahostatesman.com/sports/college/mountain-west/boise-state-university/boise-state-football/article315201970.html |
| Juelz Goff | BOIS | 0.15 | 0.12 | 2026-08-15 | https://www.ourlads.com/ncaa-football-depth-charts/depth-chart/boise-state/90130/ |
| King Miller | USC | 0.32 | 0.33 | 2026-08-01 | https://www.si.com/college/usc/football/usc-trojans-running-back-depth-competition-heating-up-fall-camp |
| Waymond Jordan | USC | 0.58 | 0.57 | 2026-08-01 | https://www.si.com/college/usc/football/usc-trojans-waymond-jordan-shares-candid-insights-injury-recovery |
| Riley Wormley | USC | 0.10 | 0.10 | 2026-08-01 | https://www.si.com/college/usc/football/usc-trojans-running-back-depth-competition-heating-up-fall-camp |
| Kamari Moulton | IOWA | 0.55 | 0.50 | 2026-08-14 | https://www.si.com/college/iowa/football/iowa-football-depth-chart-prediction-offense-week-1 |
| L.J. Phillips Jr. | IOWA | 0.45 | 0.38 | 2026-08-05 | https://www.desmoinesregister.com/story/sports/college/iowa/football/2026/08/05/iowa-football-running-back-kamari-moulton-lj-phillips/91157493007/ |

### Input audit (no rank overrides)

- L.J. Phillips vs Kamari Moulton: sourced Iowa timeshare. Marked contested; Moulton is the Week 1 favorite. FCS translation still from the ML row, not a hand-entered total.
- Malachi Toney: no sourced 2026 role change. Left as the ML WR row.
- Kaden Feagin: still TE1 after the RB conversion; no sourced receiving-role tree, so usage was not rebuilt.
- Sam Leavitt, Faizon Brandon, Keelon Russell: named-QB facts already in depth_chart; no new sourced demotion/promotion.
- Makhi Hughes and Raleek Brown: no sourced 2026 lead-job change. Left as ML + from_fcs.
- Ahmad Hardy: Drinkwitz still targeting as soon as possible / mid-September; games=10 unchanged.

## Depth-chart / news audit

- `stale_depth` Cameron Dickey: 26 days since 2026-07-30
- `stale_depth` J'Koby Williams: 53 days since 2026-07-03
- `stale_depth` Quinten Joyner: 26 days since 2026-07-30
- `stale_depth` Sire Gaines: 158 days since 2026-03-20
- `stale_depth` King Miller: 24 days since 2026-08-01
- `stale_depth` Waymond Jordan: 24 days since 2026-08-01
- `stale_depth` Riley Wormley: 24 days since 2026-08-01
- `stale_depth` Nick Osho: 21 days since 2026-08-04
- `named_starter_low_probability` Jahiem White: starter_probability=0.8
- `stale_depth` L.J. Phillips Jr.: 20 days since 2026-08-05
- `unreconciled_lead_roles` Ahmad Hardy, Jamal Roberts: MIZ RB [1.0, 0.98]

## K / D/ST

No kicking or team-defense stats in `fetch.py` (`CATEGORIES` is passing/rushing/receiving/fumbles). Not fabricated. Stream K15 / D/ST15 in the client.

## Unresolved assumptions

- No CFBD dump in this environment, so model.py was not retrained. Tuned board is a post-process of projections_2026.csv.
- Team RB pools for contested rooms use last-year rush+rec components (12-game pace) when sourced; other teams still use independent ML rows.
- Transfer translation (Nelson, Hughes, Brown, Leavitt) is still the v2 ML + from_fcs flag.
- Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; only TE scarcity and FLEX replacement changed. No sourced 2026 receiving-role split.
- Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model.
- starter_probability is blank unless a depth-chart or committee win model ran. `role` is the role score, not a probability.
- Percentiles p10/p50/p90 are managed_season_points when a scenario exists; otherwise they stay null. floor_rank/ceiling_rank still cover the full pool.
- Hardy stays at 10 games (mid-September target). Drinkwitz has not given a later date.
- Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.
- No walk-forward backtest in this pass: data/ is not present.
- Tennessee WR stack (Staley/Matthews) still comes from independent ML rows, not one team passing forecast.
