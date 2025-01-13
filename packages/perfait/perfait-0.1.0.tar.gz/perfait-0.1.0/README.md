# perfait
Performance survey comparison tool

## Concept
Visualization of multiple measurement results

### Measurement of 100 million increments
![](./images/procperf.png)

### Performance comparison of binary serializers
![](./images/serdesperf.png)

## What is possible
### procperf
1. Measuring execution time for each programming language
2. Image output of data in pivot table format

### serdesperf
1. Binary serializer performance measurement
2. Image output of data in pivot table format

## Reason for development
- I want to visualize the differences in processing speed of each programming language and performance of binary serializers

## Versions

|Version|Summary|
|:--|:--|
|0.1.0|Release perfait|

## Installation
### [perfait](https://pypi.org/project/perfait/)
`pip install perfait`

## Usage
### procperf
![](./images/procperf.png)
```json
{
  "Tick": {
    "Dtick": 200,
    "Format": "d"
  },
  "LayoutTitleText": "<b>[procperf]<br>Measurement of 100 million increments</b>",
  "XTitleText": "Elapsed time(ms)",
  "YTitleText": "Programming language",
  "Array": [
    [
      "",
      "Internal",
      "External",
      "Total"
    ],
    [
      "java<br>(openjdk 17.0.13)",
      3,
      29,
      32
    ],
    [
      "go<br>(1.19.8)",
      12,
      193,
      205
    ],
    [
      "csharp<br>(mcs 6.8.0.105)",
      42,
      26,
      68
    ],
    [
      "javascript<br>(node 18.19.0)",
      69,
      43,
      112
    ],
    [
      "cpp<br>(g++ 12)",
      166,
      5,
      171
    ],
    [
      "php<br>(8.2.26)",
      373,
      17,
      390
    ],
    [
      "python<br>(3.11.2)",
      2023,
      350,
      2373
    ],
    [
      "ruby<br>(3.1.2p20)",
      3259,
      152,
      3411
    ]
  ]
}
```

### serdesperf
![](./images/serdesperf.png)
```json
{
  "Tick": {"Dtick": 2000, "Format": "d"},
  "LayoutTitleText": "<b>[serdesperf]<br>Performance comparison of binary serializers</b>",
  "XTitleText": "",
  "YTitleText": "Binary serializer",
  "Array": [
    ["", "Ser(μs)", "Des(μs)", "Size(byte)"],
    ["Protobuf<br>double[1] first", 2560, 2115, 10],
    ["Protobuf<br>double[1]", 12, 4, 10],
    ["Protobuf<br>double[1000]", 246, 221, 8003],
    ["MessagePack<br>double[1] first", 49750, 1478, 11],
    ["MessagePack<br>double[1]", 25, 3, 11],
    ["MessagePack<br>double[1000]", 66, 95, 9004],
    ["MemoryPack<br>double[1] first", 2554, 1238, 13],
    ["MemoryPack<br>double[1]", 9, 4, 13],
    ["MemoryPack<br>double[1000]", 3, 2, 8005]
  ]
}
```

## CLI
### init
Setting up the execution time measurement code

#### 1. Initialize by running CLI
```
init
```
`perfait init`
```
perfait_scripts\measure_command.py is done.
perfait_scripts\perfait\go.mod is done.
perfait_scripts\perfait\perfait.cs is done.
perfait_scripts\perfait\perfait.go is done.
perfait_scripts\perfait\perfait.hpp is done.
perfait_scripts\perfait\perfait.java is done.
perfait_scripts\perfait\perfait.js is done.
perfait_scripts\perfait\perfait.php is done.
perfait_scripts\perfait\perfait.py is done.
perfait_scripts\perfait\perfait.rb is done.
```

### image.write
Output measurement data as an image

#### 1. Image(PNG) conversion by CLI execution
```
image.write # <perfait file path> <image file path>
```
`perfait image.write perfait.json perfait.png`
```
perfait.png is done.
```
