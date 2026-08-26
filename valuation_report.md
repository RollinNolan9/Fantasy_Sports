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
| waiver replacement | not configured (bench/IR unknown); missed weeks get 0, sensitivity below |
| stash cost | 4.0 pts when missed games ≥ 4 |

## Waiver sensitivity (bench/IR still unknown)

No hidden RB100/10.8-PPG default. Missed-week replacement on the board is 0 until bench/IR depth is set.

| extra RB bench / team | waiver rank | season pts | PPG |
|---:|---:|---:|---:|
| 0 | RB28 | 183.5 | 15.29 |
| 1 | RB42 | 170.5 | 14.21 |
| 2 | RB56 | 157.7 | 13.14 |
| 3 | RB70 | 147.6 | 12.30 |

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

Percentile columns are CDF values from probability-weighted scenarios (null where no real uncertainty model exists). p50 is the median, not the mean. floor_rank / ceiling_rank rank the full pool using p10/p90, filling unmodeled rows with managed_season_points.

Comparison baseline is `projections_2026_tuned(3).csv` only.

## 28 / 35 / 42 QB sensitivity (top 15 QBs by draft-adjusted value)

 rank                name team  projected_points_if_active  starter_vorp  qb35_adjusted_value  qb42_adjusted_value  draft_adjusted_value
    2         Byrum Brown  AUB                       313.9          68.8                 85.6                 89.9                  89.9
    3      Conner Weigman  HOU                       312.1          67.0                 83.8                 88.1                  88.1
    4        Brad Jackson TXST                       310.0          64.9                 81.7                 86.0                  86.0
   12       Devon Dampier UTAH                       286.4          41.3                 58.1                 62.4                  62.4
   13       Avery Johnson  KSU                       280.3          35.2                 52.0                 56.3                  56.3
   15         Marcel Reed TA&M                       279.9          34.8                 51.6                 55.9                  55.9
   18       Bryson Barnes  USU                       273.4          28.3                 45.1                 49.4                  49.4
   22       Colton Joseph  WIS                       269.6          24.5                 41.3                 45.6                  45.6
   37      Bear Bachmeier  BYU                       260.9          15.8                 32.6                 36.9                  36.9
   39  Trinidad Chambliss MISS                       259.7          14.6                 31.4                 35.7                  35.7
   43      Nick Minicucci  DEL                       257.9          12.8                 29.6                 33.9                  33.9
   44 Demond Williams Jr. WASH                       257.7          12.6                 29.4                 33.7                  33.7
   45         Liam Szarka   AF                       257.2          12.1                 28.9                 33.2                  33.2
   46        Arch Manning  TEX                       256.9          11.8                 28.6                 32.9                  32.9
   48          Broc Lowry  WMU                       255.4          10.3                 27.1                 31.4                  31.4

## Before / after top 150 (tuned(3) → tuned(4))

tuned(3) top 15:

 rank            name position  proj_points  draft_value
    1      Kewan Lacy       RB        252.6         94.9
    2     Byrum Brown       QB        313.9         89.9
    3  Conner Weigman       QB        312.1         88.1
    4    Brad Jackson       QB        310.0         86.0
    5       LJ Martin       RB        240.4         82.7
    6        Cam Cook       RB        231.2         73.5
    7 Jordan Marshall       RB        225.0         67.3
    8   DeSean Bishop       RB        224.2         66.5
    9    Evan Dickens       RB        224.1         66.4
   10  Jai'Den Thomas       RB        223.5         65.8
   11     Beau Sparks       WR        214.9         63.4
   12   Devon Dampier       QB        286.4         62.4
   13     Ahmad Hardy       RB        194.7         58.6
   14   Avery Johnson       QB        280.3         56.3
   15  Antwan Raymond       RB        213.9         56.2

tuned(4) top 150 (old_rank is tuned(3)):

 rank playerId                        name team position pos_rank  proj_points  managed_vorp  starter_vorp  draft_adjusted_value  role  old_rank
    1  5086388                  Kewan Lacy MISS       RB      RB1        252.6          94.9          94.9                  94.9  1.00         1
    2  4880272                 Byrum Brown  AUB       QB      QB1        313.9          68.8          68.8                  89.9  1.00         2
    3  4685574              Conner Weigman  HOU       QB      QB2        312.1          67.0          67.0                  88.1  1.00         3
    4  5148803                Brad Jackson TXST       QB      QB3        310.0          64.9          64.9                  86.0  1.00         4
    5  4918126                   LJ Martin  BYU       RB      RB2        240.4          82.7          82.7                  82.7  1.00         5
    6  4918103                    Cam Cook  WVU       RB      RB3        231.2          73.5          73.5                  73.5  1.00         6
    7  5079574             Jordan Marshall MICH       RB      RB4        225.0          67.3          67.3                  67.3  1.00         7
    8  4921108               DeSean Bishop TENN       RB      RB5        224.2          66.5          66.5                  66.5  1.00         8
    9  5076122                Evan Dickens   BC       RB      RB6        224.1          66.4          66.4                  66.4  1.00         9
   10  5125754              Jai'Den Thomas UNLV       RB      RB7        223.5          65.8          65.8                  65.8  1.00        10
   11  5152414                 Beau Sparks TXST       WR      WR1        214.9          57.2          63.4                  63.4  1.00        11
   12  5105849               Devon Dampier UTAH       QB      QB4        286.4          41.3          41.3                  62.4  1.00        12
   13  4870857               Avery Johnson  KSU       QB      QB5        280.3          35.2          35.2                  56.3  1.00        14
   14  5209945              Antwan Raymond RUTG       RB      RB8        213.9          56.2          56.2                  56.2  1.00        15
   15  4870971                 Marcel Reed TA&M       QB      QB6        279.9          34.8          34.8                  55.9  1.00        16
   16  5223167          Will Henderson III UTSA       RB      RB9        213.4          55.7          55.7                  55.7  1.00        17
   17  5079720              Jeremiah Smith  OSU       WR      WR2        207.1          49.4          55.6                  55.6  1.00        18
   18  4695600               Bryson Barnes  USU       QB      QB7        273.4          28.3          28.3                  49.4  1.00        19
   19  5132629              Braylon Staley TENN       WR      WR3        200.5          42.8          49.0                  49.0  1.00        20
   20  5092811                   CJ Miller  TOL       RB     RB10        205.6          47.9          47.9                  47.9  1.00        21
   21  5173431             Wayshawn Parker UTAH       RB     RB11        205.5          47.8          47.8                  47.8  1.00        22
   22  5125715               Colton Joseph  WIS       QB      QB8        269.6          24.5          24.5                  45.6  1.00        23
   23  5258016               Caleb Hawkins OKST       RB     RB12        202.6          44.9          44.9                  44.9  1.00        24
   24  5079580               Mike Matthews TENN       WR      WR4        195.1          37.4          43.6                  43.6  1.00        25
   25  4431328          Rodney Hammond Jr.  SAC       RB     RB13        201.0          43.3          43.3                  43.3  1.00        26
   26  5030333           Sedrick Alexander  VAN       RB     RB14        198.8          41.1          41.1                  41.1  1.00        28
   27  5079345                Mario Craver TA&M       WR      WR5        192.3          34.6          40.8                  40.8  1.00        29
   28  5141423              Jordon Davison  ORE       RB     RB15        198.2          40.5          40.5                  40.5  1.00        30
   29  5079663                Jeremy Payne  TCU       RB     RB16        197.7          40.0          40.0                  40.0  1.00        31
   30  5084771                     KJ Duff RUTG       WR      WR6        191.0          33.3          39.5                  39.5  1.00        32
   31  5086034                 Cam Edwards  MSU       RB     RB17        197.0          39.3          39.3                  39.3  1.00        33
   32  4914830               Easton Messer  FAU       WR      WR7        190.4          32.7          38.9                  38.9  1.00        34
   33  4911971                Jahiem White  UNT       RB     RB18        196.0          38.3          38.3                  38.3  1.00        35
   34  5220197              Fluff Bothwell MSST       RB     RB19        195.6          37.9          37.9                  37.9  1.00        36
   35  5159175               Malachi Toney  MIA       WR      WR8        189.4          31.7          37.9                  37.9  1.00        37
   36  5141517                  Bo Jackson  OSU       RB     RB20        194.8          37.1          37.1                  37.1  1.00        38
   37  5141367              Bear Bachmeier  BYU       QB      QB9        260.9          15.8          15.8                  36.9  1.00        39
   38  5077060                Amare Thomas  HOU       WR      WR9        188.3          30.6          36.8                  36.8  1.00        40
   39  4911529          Trinidad Chambliss MISS       QB     QB10        259.7          14.6          14.6                  35.7  1.00        41
   40  5079742             Aneyas Williams   ND       RB     RB21        193.4          35.7          35.7                  35.7  1.00        42
   41  5164332               Nate Sheppard DUKE       RB     RB22        192.8          35.1          35.1                  35.1  1.00        43
   42  5197065                 Ahmad Hardy  MIZ       RB     RB23        192.0          34.3          72.7                  34.3  1.00        13
   43  5153846              Nick Minicucci  DEL       QB     QB11        257.9          12.8          12.8                  33.9  1.00        44
   44  5079653         Demond Williams Jr. WASH       QB     QB12        257.7          12.6          12.6                  33.7  1.00        45
   45  5238868                 Liam Szarka   AF       QB     QB13        257.2          12.1          12.1                  33.2  1.00        46
   46  4870906                Arch Manning  TEX       QB     QB14        256.9          11.8          11.8                  32.9  1.00        47
   47  5078244              Caleb Komolafe   NU       RB     RB24        190.5          32.8          32.8                  32.8  1.00        48
   48  5074245                  Broc Lowry  WMU       QB     QB15        255.4          10.3          10.3                  31.4  1.00        49
   49  4685578             Gunner Stockton  UGA       QB     QB16        254.9           9.8           9.8                  30.9  1.00        50
   50  4801717                 Noah Fifita ARIZ       QB     QB17        254.7           9.6           9.6                  30.7  1.00        51
   51  4915980                 John Mateer   OU       QB     QB18        254.4           9.3           9.3                  30.4  1.00        52
   52  5085006               Jalen Buckley  WMU       RB     RB25        186.5          28.8          28.8                  28.8  1.00        53
   53  5114311              Jackson Harris  LSU       WR     WR10        180.3          22.6          28.8                  28.8  0.98        54
   54  5080403               Jaylen Raynor  ISU       QB     QB19        252.5           7.4           7.4                  28.5  1.00        55
   55  5079322                 Jadan Baugh  FLA       RB     RB26        185.5          27.8          27.8                  27.8  1.00        56
   56  4816099                Javen Jacobs  USU       RB     RB27        185.4          27.7          27.7                  27.7  1.00        57
   57  5079369                     CJ Carr   ND       QB     QB20        251.6           6.5           6.5                  27.6  1.00        58
   58  4911929          Alonza Barnett III  UCF       QB     QB21        251.1           6.0           6.0                  27.1  0.98        59
   59  5044387           Anthony Colandrea  NEB       QB     QB22        250.0           4.9           4.9                  26.0  1.00        60
   60  5079349                 Isaac Brown  LOU       RB     RB28        183.5          25.8          25.8                  25.8  1.00        61
   61  4870513               Maddux Madsen BOIS       QB     QB23        249.4           4.3           4.3                  25.4  1.00        62
   62  5167252                Duncan Brune OHIO       RB     RB29        183.0          25.3          25.3                  25.3  1.00        63
   63  4869991              Caden Veltkamp  FAU       QB     QB24        248.9           3.8           3.8                  24.9  1.00        64
   64  4870760              Justice Haynes   GT       RB     RB30        182.4          24.7          24.7                  24.7  1.00        65
   65  5218633                  Ryan Wingo  TEX       WR     WR11        176.0          18.3          24.5                  24.5  1.00        66
   66  4870934             Rueben Owens II TA&M       RB     RB31        181.9          24.2          24.2                  24.2  1.00        67
   67  5084582                 Jordan Gant  AKR       RB     RB32        181.8          24.1          24.1                  24.1  1.00        68
   68  4838536                Tyler Hughes  WYO       QB     QB25        247.8           2.7           2.7                  23.8  0.99        69
   69  5125823                 DJ McKinney TLSA       RB     RB33        181.5          23.8          23.8                  23.8  0.99        70
   70  4912453                Lucky Sutton SDSU       RB     RB34        181.0          23.3          23.3                  23.3  1.00        71
   71  5177084              Kamario Taylor MSST       QB     QB26        247.1           2.0           2.0                  23.1  0.96        72
   72  5079712                Julian Sayin  OSU       QB     QB27        246.8           1.7           1.7                  22.8  1.00        73
   73  5088153                Micahi Danzy  FSU       WR     WR12        173.6          15.9          22.1                  22.1  1.00        74
   74  5193580              Cameron Dickey  TTU       RB     RB35        179.6          21.9          21.9                  21.9  0.70        27
   75  5154734               Griffin Wilde   NU       WR     WR13        173.0          15.3          21.5                  21.5  1.00        75
   76  4685454               Jayden Maiava  USC       QB     QB28        245.2           0.1           0.1                  21.2  1.00        76
   77  5307005              Mason McKenzie   BC       QB     QB29        245.1           0.0          -0.1                  21.1  0.82        77
   78  5141677            Ja'Kyrian Turner PITT       RB     RB36        178.6          20.9          20.9                  20.9  1.00        78
   79  5122157                 Caden Creel JXST       QB     QB30        244.3          -0.8          -0.9                  20.3  1.00        79
   80  5126468                Will Hammond  TTU       QB     QB31        243.7          -1.4          -1.5                  19.7  0.95        80
   81  5125900                  Joshua Dye MISS       RB     RB37        176.8          19.1          19.1                  19.1  0.92        81
   82  5153885               Rodney Nelson M-OH       RB     RB38        176.1          18.4          18.4                  18.4  0.70        82
   83  4920901               Darius Taylor MINN       RB     RB39        175.4          17.7          17.7                  17.7  1.00        83
   84  5084047                Nate Frazier  UGA       RB     RB40        174.3          16.6          16.6                  16.6  1.00        84
   85  5083042             Skyler Locklear MOST       QB     QB32        238.8          -6.3          -6.4                  14.8  1.00        85
   86  4912342                Wayne Knight UCLA       RB     RB41        171.2          13.5          13.5                  13.5  1.00        86
   87  5295318              Waymond Jordan  USC       RB     RB42        170.5          12.8          12.8                  12.8  0.70       218
   88  5150297                Cale Hellums ARMY       QB     QB33        236.7          -8.4          -8.5                  12.7  1.00        87
   89  5226019               Caden Pinnick  WSU       QB     QB34        236.6          -8.5          -8.6                  12.6  0.97        88
   90  5077502               Carson Hansen  PSU       RB     RB43        169.9          12.2          12.2                  12.2  1.00        89
   91  5148787                 Wyatt Young OKST       WR     WR14        163.7           6.0          12.2                  12.2  1.00        90
   92  4871076          Quintrevion Wisner  FSU       RB     RB44        168.5          10.8          10.8                  10.8  1.00        91
   93  5079687                Jordan Shipp  UNC       WR     WR15        162.2           4.5          10.7                  10.7  1.00        92
   94  4870736           Mark Fletcher Jr.  MIA       RB     RB45        167.8          10.1          10.1                  10.1  1.00        93
   95  5084135              Pofele Ashlock  HAW       WR     WR16        160.5           2.8           9.0                   9.0  1.00        94
   96  4918108               Jordan Napier SDSU       WR     WR17        159.5           1.8           8.0                   8.0  1.00        95
   97  5152158             Deuce Alexander MISS       WR     WR18        159.5           1.8           8.0                   8.0  1.00        96
   98  5152815               Danny Scudero COLO       WR     WR19        157.6          -0.1           6.1                   6.1  1.00        98
   99  4832804                Jordan Dwyer  TCU       WR     WR20        157.4          -0.3           5.9                   5.9  1.00        99
  100  5078144             Landen Chambers  UCF       RB     RB46        163.0           5.3           5.3                   5.3  0.93       100
  101  5121879           Keshaun Singleton  AUB       WR     WR21        156.4          -1.3           4.9                   4.9  1.00       101
  102  5158343             Braxton Woodson NAVY       QB     QB35        228.5         -16.6         -16.7                   4.5  1.00       102
  103  5078165             Junior Sherrill  VAN       WR     WR22        156.0          -1.7           4.5                   4.5  1.00       103
  104  5171031                  Matt Vezza OHIO       QB     QB36        228.3         -16.8         -16.9                   4.3  1.00       104
  105  4870922               Duce Robinson  FSU       WR     WR23        155.7          -2.0           4.2                   4.2  1.00       105
  106  5094032                  Nico Brown STAN       WR     WR24        155.2          -2.5           3.7                   3.7  0.96       106
  107  5153730                Jaden Barnes  CLT       WR     WR25        155.1          -2.6           3.6                   3.6  1.00       107
  108  5141711       Ryan Coleman-Williams  ALA       WR     WR26        154.7          -3.0           3.2                   3.2  1.00       108
  109  5219834             Drew Mestemaker OKST       QB     QB37        227.1         -18.0         -18.1                   3.1  1.00       109
  110  4870728                Kaden Feagin  ILL       TE      TE1        160.8           3.1           3.1                   3.1  1.00       110
  111  5146725        Kaden Shields-Dutton  FAU       RB     RB47        160.6           2.9           2.9                   2.9  0.98       111
  112  5143191                  Micah Ford STAN       RB     RB48        160.4           2.7           2.7                   2.7  1.00       112
  113  5154284            Ramone Green Jr. MOST       RB     RB49        160.4           2.7           2.7                   2.7  1.00       113
  114  4685445                Rayshon Luke FRES       RB     RB50        160.3           2.6           2.6                   2.6  1.00       114
  115  5227209          Anthony Reagan Jr.   UL       RB     RB51        160.3           2.6           2.6                   2.6  0.99       115
  116  4685696                Beau Pribula  UVA       QB     QB38        226.3         -18.8         -18.9                   2.3  0.96       116
  117  4871010         Shelton Sampson Jr.   UL       WR     WR27        153.8          -3.9           2.3                   2.3  1.00       117
  118  4804878              Cooper Barkate  MIA       WR     WR28        153.6          -4.1           2.1                   2.1  1.00       118
  119  4805256                Sutton Smith  ARK       RB     RB52        159.7           2.0           2.0                   2.0  1.00       119
  120  4869582                Cam Barfield  HAW       RB     RB53        159.3           1.6           1.6                   1.6  1.00       120
  121  4689529             Kenji Christian CONN       RB     RB54        159.2           1.5           1.5                   1.5  1.00       121
  122  5159948           Chris Johnson Jr. CLEM       RB     RB55        159.2           1.5           1.5                   1.5  1.00       122
  123  5084769                Angel Flores  CMU       QB     QB39        225.1         -20.0         -20.1                   1.1  1.00       123
  124  5141695            Malik Washington   MD       QB     QB40        224.9         -20.2         -20.3                   0.9  1.00       124
  125  4801299                 Rocco Becht  PSU       QB     QB41        224.4         -20.7         -20.8                   0.4  1.00       125
  126  5084084              Kevin Jennings  SMU       QB     QB42        224.2         -20.9         -21.0                   0.2  1.00       126
  127  4795295                Katin Houser  ILL       QB     QB43        224.0         -21.1         -21.2                   0.0  1.00       127
  128  5079506                 Daniel Hill  ALA       RB     RB56        157.7           0.0          -1.5                   0.0  1.00       128
  129  5080703          Isaiah Sategna III   OU       WR     WR29        151.5          -6.2          -2.1                   0.0  1.00       129
  130  5141586              Dakorien Moore  ORE       WR     WR30        151.2          -6.5          -2.4                  -0.3  1.00       130
  131  5224764                 Sean Wilson  DEL       WR     WR31        151.2          -6.5          -2.4                  -0.3  0.98       131
  132  5146724               Turbo Richard   IU       RB     RB57        157.2          -0.5          -2.0                  -0.5  1.00       132
  133  4881032               Taron Dickens  NIU       QB     QB44        223.2         -21.9         -22.0                  -0.8  0.95       133
  134  5193302           Telly Johnson Jr.  NIU       RB     RB58        156.7          -1.0          -2.5                  -1.0  1.00       134
  135  4907671           Anthony Evans III MSST       WR     WR32        150.3          -7.4          -3.3                  -1.2  1.00       135
  136  5079301                   CJ Bailey NCSU       QB     QB45        222.4         -22.7         -22.8                  -1.6  1.00       136
  137  4869553            Bishop Davenport  USA       QB     QB46        222.2         -22.9         -23.0                  -1.8  1.00       137
  138  5101124               Micah Alejado  HAW       QB     QB47        222.2         -22.9         -23.0                  -1.8  1.00       138
  139  4685237               Michael Allen  ECU       RB     RB59        155.8          -1.9          -3.4                  -1.9  0.95       139
  140  4871091              Lunch Winfield   UL       QB     QB48        221.7         -23.4         -23.5                  -2.3  1.00       140
  141  5150424               Jordan Faison   ND       WR     WR33        149.1          -8.6          -4.5                  -2.4  1.00       141
  142  4870642               Jeremiah Cobb  AUB       RB     RB60        155.0          -2.7          -4.2                  -2.7  1.00       142
  143  5078312               Nyziah Hunter  NEB       WR     WR34        147.9          -9.8          -5.7                  -3.6  1.00       143
  144  5156906                  Bill Davis   VT       RB     RB61        153.9          -3.8          -5.3                  -3.8  1.00       144
  145  5141572                Andrew Marsh MICH       WR     WR35        147.1         -10.6          -6.5                  -4.4  0.99       145
  146  5194795 Na'eem Abdul-Rahim Gladding   MD       WR     WR36        145.9         -11.8          -7.7                  -5.6  0.99       146
  147  5121169               Darian Mensah  MIA       QB     QB49        218.1         -27.0         -27.1                  -5.9  1.00       147
  148  5075805                Aidan Chiles   NU       QB     QB50        217.7         -27.4         -27.5                  -6.3  1.00       148
  149  5155532                Sawyer Seidl WAKE       RB     RB62        151.4          -6.3          -7.8                  -6.3  1.00       149
  150  5084409            Jared Richardson DUKE       WR     WR37        145.2         -12.5          -8.4                  -6.3  0.96       150

## 20 largest risers (better rank)

- Riley Wormley (RB USC): 3109 → 1597  proj 12.9→44.5
- Kamari Moulton (RB IOWA): 1102 → 285  proj 66.7→126.8; committee/split scenario
- Quinten Joyner (RB TTU): 1669 → 866  proj 42.1→80.0
- King Miller (RB USC): 988 → 258  proj 73.1→129.9; committee/split scenario
- L.J. Phillips Jr. (RB IOWA): 897 → 387  proj 78.0→114.8; committee/split scenario
- Waymond Jordan (RB USC): 218 → 87  proj 137.2→170.5; committee/split scenario
- J'Koby Williams (RB TTU): 276 → 200  proj 127.6→141.7; committee/split scenario
- Trinidad Chambliss (QB MISS): 41 → 39  QB42 vs starter VORP
- Mario Craver (WR TA&M): 29 → 27  lineup-optimizer VORP vs old per-position replacement
- Bear Bachmeier (QB BYU): 39 → 37  QB42 vs starter VORP
- Jahiem White (RB UNT): 35 → 33  lineup-optimizer VORP vs old per-position replacement
- Nate Sheppard (RB DUKE): 43 → 41  lineup-optimizer VORP vs old per-position replacement
- Sedrick Alexander (RB VAN): 28 → 26  lineup-optimizer VORP vs old per-position replacement
- Cam Edwards (RB MSU): 33 → 31  lineup-optimizer VORP vs old per-position replacement
- Jeremy Payne (RB TCU): 31 → 29  lineup-optimizer VORP vs old per-position replacement
- Easton Messer (WR FAU): 34 → 32  lineup-optimizer VORP vs old per-position replacement
- Fluff Bothwell (RB MSST): 36 → 34  lineup-optimizer VORP vs old per-position replacement
- Malachi Toney (WR MIA): 37 → 35  lineup-optimizer VORP vs old per-position replacement
- Jordon Davison (RB ORE): 30 → 28  lineup-optimizer VORP vs old per-position replacement
- Bo Jackson (RB OSU): 38 → 36  lineup-optimizer VORP vs old per-position replacement

## 20 largest fallers (worse rank)

- Dylan Riley (RB BOIS): 97 → 229  proj 165.6→134.6; committee/split scenario
- Cameron Dickey (RB TTU): 27 → 74  proj 200.9→179.6; committee/split scenario
- Ahmad Hardy (RB MIZ): 13 → 42  managed replacement on 2 missed games
- Faizon Brandon (QB TENN): 271 → 273  named-QB prior; QB42 vs starter VORP
- Cutter Boley (QB ASU): 287 → 289  QB42 vs starter VORP
- Luke Weaver (QB SJSU): 296 → 298  named-QB prior; QB42 vs starter VORP
- Jacurri Brown (QB RICE): 300 → 302  QB42 vs starter VORP
- Rickie Collins (QB KENN): 293 → 295  QB42 vs starter VORP
- Kam Thomas (RB UTEP): 262 → 264  lineup-optimizer VORP vs old per-position replacement
- Tre' Brown (WR LSU): 261 → 263  lineup-optimizer VORP vs old per-position replacement
- Mudia Reuben (WR USF): 259 → 261  lineup-optimizer VORP vs old per-position replacement
- Dalton Stroman (WR APP): 263 → 265  lineup-optimizer VORP vs old per-position replacement
- Javon Tracy (WR MINN): 264 → 266  lineup-optimizer VORP vs old per-position replacement
- London Montgomery (RB FLA): 257 → 259  lineup-optimizer VORP vs old per-position replacement
- Javin Gordon (RB TENN): 258 → 260  lineup-optimizer VORP vs old per-position replacement
- Brock Spalding (WR ECU): 260 → 262  lineup-optimizer VORP vs old per-position replacement
- Herschel Turner (RB NEV): 268 → 270  lineup-optimizer VORP vs old per-position replacement
- DeAndre Moore Jr. (WR COLO): 265 → 267  lineup-optimizer VORP vs old per-position replacement
- Adrian Norton (WR MRSH): 266 → 268  lineup-optimizer VORP vs old per-position replacement
- Dre'lon Miller (WR BAY): 267 → 269  lineup-optimizer VORP vs old per-position replacement

## Player-level regression diagnostics

Drivers only. Not forced to consensus.

Potentially underprojected:
- Malachi Toney (WR MIA): rank 37→35; pts 189.4→189.4; ppg 15.78; games 12; role 1.00; start_p nan; WR29 draft baseline
- Jordan Marshall (RB MICH): rank 7→7; pts 225.0→225.0; ppg 18.75; games 12; role 1.00; start_p 0.90
- Sam Leavitt (QB LSU): rank 255→256; pts 196.3→196.3; ppg 16.36; games 12; role 0.92; start_p nan
- Isaiah Sategna III (WR OU): rank 129→129; pts 151.5→151.5; ppg 12.62; games 12; role 1.00; start_p nan; WR29 draft baseline
- Keelon Russell (QB ALA): rank 376→378; pts 181.6→181.6; ppg 15.13; games 12; role 1.00; start_p 1.00; named-QB prior
- David McComb (QB M-OH): rank 380→382; pts 181.5→181.5; ppg 15.12; games 12; role 1.00; start_p 1.00; named-QB prior
- Makhi Hughes (RB HOU): rank 397→400; pts 113.7→113.7; ppg 9.48; games 12; role 0.93; start_p nan
- Raleek Brown (RB TEX): rank 674→677; pts 91.4→91.4; ppg 7.62; games 12; role 0.90; start_p nan

Potentially overprojected:
- Nick Osho (RB UNT): rank 244→245; pts 131.3→131.3; ppg 10.94; games 12; role 0.70; start_p 0.25; committee budget split
- Kaden Feagin (TE ILL): rank 110→110; pts 160.8→160.8; ppg 13.40; games 12; role 1.00; start_p 1.00; FLEX replacement (no TE premium)
- L.J. Phillips Jr. (RB IOWA): rank 897→387; pts 78.0→114.8; ppg 9.57; games 12; role 0.70; start_p 0.45; committee budget split
- Cameron Dickey (RB TTU): rank 27→74; pts 200.9→179.6; ppg 14.96; games 12; role 0.70; start_p 0.50; committee budget split
- J'Koby Williams (RB TTU): rank 276→200; pts 127.6→141.7; ppg 11.81; games 12; role 0.70; start_p 0.33; committee budget split
- Braylon Staley (WR TENN): rank 20→19; pts 200.5→200.5; ppg 16.71; games 12; role 1.00; start_p nan; WR29 draft baseline
- Mike Matthews (WR TENN): rank 25→24; pts 195.1→195.1; ppg 16.26; games 12; role 1.00; start_p nan; WR29 draft baseline
- Ahmad Hardy (RB MIZ): rank 13→42; pts 194.7→192.0; ppg 19.20; games 10; role 1.00; start_p 1.00; injury/ramp + waiver missed-games

## Contested backfield distributions

Percentiles are CDF(managed scale) of winner-scenario points. Volume (rush att/yds/TD, rec/yds/TD) is allocated first then scored at 0.5 PPR. role is unchanged. Leftover backs keep null starter_probability.

### TTU (budget=408.3, shares=1.000, P(win)=1.000)

playerId                  name  managed_season_points  expected_opportunity_share  starter_probability       p10        p50        p75        p90
 5193580        Cameron Dickey                  179.6                    0.439715                 0.50 80.930602 100.257313 265.422857 265.422857
 5086393       J'Koby Williams                  141.7                    0.347119                 0.33 56.823614  88.987925 265.422857 265.422857
 4917949        Quinten Joyner                   80.0                    0.195938                 0.17 36.263284  45.842264  45.842264 265.422857
 5290564         Ashton Rowden                    2.3                    0.005561                  NaN  1.667613   2.065848   2.611544   2.611544
 5310308        Loic Tshibangu                    2.3                    0.005556                  NaN  1.665934   2.063768   2.608915   2.608915
 5196027 Michael Henderson III                    1.6                    0.004021                  NaN  1.205791   1.493741   1.888314   1.888314
 5385737      Sawyer Wilkerson                    0.9                    0.002089                  NaN       NaN        NaN        NaN        NaN

### BOIS (budget=304.0, shares=1.000, P(win)=1.000)

playerId              name  managed_season_points  expected_opportunity_share  starter_probability       p10       p50        p75        p90
 5146712       Dylan Riley                  134.6                    0.442727                 0.50 58.041818 77.389091 197.618571 197.618571
 5147379       Sire Gaines                  110.1                    0.362207                 0.35 41.112955 69.575769 197.618571 197.618571
 5124975        Juelz Goff                   48.7                    0.160157                 0.15 19.347273 24.556154  24.556154 197.618571
 5126514 Harry Stewart III                    4.5                    0.014670                  NaN  3.048999  4.065332   5.159845   5.159845
 5244754    Keilan Chavies                    2.6                    0.008570                  NaN  1.781202  2.374936   3.014342   3.014342
 5274323     Mariyon Sloan                    2.1                    0.006993                  NaN  1.453461  1.937948   2.459703   2.459703
 5295045     Zeke Martinez                    1.4                    0.004675                  NaN  0.971565  1.295420   1.644187   1.644187

### USC (budget=344.9, shares=1.000, P(win)=1.000)

playerId             name  managed_season_points  expected_opportunity_share  starter_probability       p10        p50        p75        p90
 5295318   Waymond Jordan                  170.5                4.944502e-01                 0.58 76.444307 224.160000 224.160000 224.160000
 5233016      King Miller                  129.9                3.766240e-01                 0.32 44.257231  92.631412 224.160000 224.160000
 5144164    Riley Wormley                   44.5                1.289257e-01                 0.10 18.015155  28.070125  28.070125  28.070125
 5158934     Shahn Alston                    0.0                6.781461e-10                  NaN       NaN        NaN        NaN        NaN
 5159076 Deshonne Redeaux                    0.0                6.781461e-10                  NaN       NaN        NaN        NaN        NaN
 5233015    Cian McKelvey                    0.0                6.781461e-10                  NaN       NaN        NaN        NaN        NaN
 5386510     Kayne Miller                    0.0                6.781461e-10                  NaN       NaN        NaN        NaN        NaN
 5386511       Tyson Park                    0.0                6.781461e-10                  NaN       NaN        NaN        NaN        NaN

### IOWA (budget=261.7, shares=1.000, P(win)=1.000)

playerId              name  managed_season_points  expected_opportunity_share  starter_probability       p10        p50        p75        p90
 5093886    Kamari Moulton                  126.8                    0.484516                 0.55 73.858895 170.086485 170.086485 170.086485
 5155048 L.J. Phillips Jr.                  114.8                    0.438800                 0.45 69.604623  69.604623 170.086485 170.086485
 5142226   Xavier Williams                    6.1                    0.023263                  NaN  5.377519   6.668124   6.668124   6.668124
 5142261       Brevin Doll                    4.6                    0.017699                  NaN  4.091371   5.073299   5.073299   5.073299
 5246572     Nathan McNeil                    3.8                    0.014647                  NaN  3.385845   4.198448   4.198448   4.198448
 5198313     O'Lontae Dean                    2.9                    0.011252                  NaN  2.600892   3.225106   3.225106   3.225106
 5295539   Braeden Jackson                    2.6                    0.009822                  NaN  2.270508   2.815430   2.815430   2.815430


## RB-room validation

Scoring, replacement levels, and valuation formulas were not changed (scoring_ppr=0.5, WR29=151.5, FLEX=157.7, QB28/35/42=245.1/228.3/224.0).

`starter_probability` is P(win the RB job) in modeled rooms (sums to 1.0) or a sourced named-starter probability. It is blank when no probability model ran. `role` remains the role score. `breakout_probability` is 0 for the favorite and P(win) for others in the room — not an alias of role or role_confidence.

### Targeted audits (ranges, not hardcoded outputs)

- PASS USC RB room: 344.9 vs 335–355
- PASS Waymond Jordan: 170.5 vs 170–180 (rank 87, share 0.494, P(win) 0.58)
- MISS King Miller: 129.9 vs 140–155 (rank 258, share 0.377, P(win) 0.32)
- PASS Iowa RB room: 261.6 vs 260–300
- MISS L.J. Phillips Jr.: 114.8 vs 115–145 (rank 387, share 0.439, P(win) 0.45)
- PASS Kamari Moulton: 126.8 vs 110–135 (rank 285, share 0.485, P(win) 0.55)

Miller is below the 140–155 band because a 32% P(win) / 0.33 workload against Jordan's 0.58 / 0.57, plus Wormley's 10% winner scenario, yields ~0.38 expected share of a 345-point when-playing pool. That is the volume-first math, not a rank override. Phillips is 0.2 below the 115 floor on the same rule (FCS volume is not added to Iowa's pool).

### Team RB point pool and share sum

| team | before pool | after pool | before share sum | after share sum | after P(win) |
|---|---:|---:|---:|---:|---:|
| BOIS | 304.1 | 304.0 | 1.000 | 1.000 | 1.000 |
| IOWA | 150.1 | 261.7 | 1.001 | 1.000 | 1.000 |
| TTU | 372.4 | 408.3 | 1.001 | 1.000 | 1.000 |
| USC | 223.2 | 344.9 | 1.000 | 1.000 | 1.000 |

### Top-112 / top-126 positional composition

| cut | when | QB | RB | WR | TE |
|---|---|---:|---:|---:|---:|
| top 112 | before | 37 | 48 | 26 | 1 |
| top 112 | after | 37 | 48 | 26 | 1 |
| top 126 | before | 42 | 55 | 28 | 1 |
| top 126 | after | 42 | 55 | 28 | 1 |

### Players entering top 150

- Waymond Jordan (RB USC) rank 87

### Players leaving top 150

- Dylan Riley (RB BOIS) was rank 97

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

- L.J. Phillips vs Kamari Moulton: sourced Iowa timeshare. Marked contested; Moulton is the Week 1 favorite. Phillips's FCS 2025 volume is in opportunity.csv with same_2026_team=False so it does not inflate Iowa's pool.
- Malachi Toney: no sourced 2026 role change. Left as the ML WR row.
- Kaden Feagin: still TE1 after the RB conversion; no sourced receiving-role tree, so usage was not rebuilt.
- Sam Leavitt, Faizon Brandon, Keelon Russell: named-QB facts already in depth_chart; no new sourced demotion/promotion.
- Makhi Hughes and Raleek Brown: no sourced 2026 lead-job change. Left as ML + from_fcs.
- Ahmad Hardy: Drinkwitz still targeting as soon as possible / mid-September; games=10 unchanged. Missed-week replacement is 0 until bench/IR is configured (see waiver sensitivity).
- King Miller receiving (16-111-0 in 2025) was added to opportunity.csv; it was previously unsourced and treated as 0.

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

## K / D/ST

No kicking or team-defense stats in `fetch.py` (`CATEGORIES` is passing/rushing/receiving/fumbles). Not fabricated. Stream K15 / D/ST15 in the client.

## Unresolved assumptions

- No CFBD dump in this environment, so model.py was not retrained. Tuned board is a post-process of projections_2026.csv.
- Team RB pools use sourced last-year components in opportunity.csv, paced to 12 games from when-playing rates (samples under 6 games are residual share only).
- Pass-attempt reconciliation is only the dual-QB snap split; WRs still have independent ML rows (no team target tree).
- Transfer translation (Nelson, Hughes, Brown, Leavitt, Phillips FCS→Iowa) is still the v2 ML + from_fcs flag. Phillips's FCS volume is not added to Iowa's pool.
- Feagin's RB→TE usage (routes/targets vs 122 carries) is not reprojected; only TE scarcity and FLEX replacement changed.
- Named-QB prior is a blend toward 0.90×QB29, not a recruiting/scheme volume model. It does not invent percentiles.
- starter_probability is blank unless a depth-chart or committee win model ran. Null is not written as 0. role is the role score.
- breakout_probability is P(win) for the non-favorite in a modeled room and 0 for the favorite; it is not a league-wide breakout model.
- role_confidence comes from depth_chart confidence (high/medium/low). Blank when unsourced.
- Bench/IR depth is unknown, so waiver replacement is 0 on the board and sensitivity is reported instead of a hidden RB100 default.
- Hardy stays at 10 games (mid-September target). Drinkwitz has not given a later date.
- Fantrax 2RR / return TD / K / D/ST still absent from the stat extract.
- No walk-forward backtest in this pass: data/ is not present.
