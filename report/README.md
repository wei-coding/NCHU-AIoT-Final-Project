# AIOT 智慧物聯網期末報告

## 動機

目前在台灣自駕族的數量仍不少，在車上絕大部分時間都是聽廣播電台的音樂，又或是自己將手機連接到車用電腦上播放。但即便是使用手機播放可能已經挑選過的歌單，難免還是會出現「現在不想聽這首歌」的情況，我們團隊討論過後發現，這問題與當下情緒最有關連。

假設以下情境：某駕駛人在塞車時，因為平常聽的音樂都屬於比較高亢的歌，在這時串流軟體當然也推薦類似的曲風，但駕駛人卻會因為音樂太過於吵雜而更容易發怒，甚至影響到駕駛安全。

不只是在車上，其實在各個場景，適合的音樂都可以讓我們的心情更好，效率更高。因此我們想透過觀測人的情緒，給出在當下情緒適合聽的歌曲或曲風分類。

## 相關實做

我們有查到的實做部分，主要有兩大類，分別是音樂串流軟體的音樂推薦演算法，和ECG分析情緒類型。前者的問題是，推薦演算法只能根據以往所聽的音樂類型給出建議，但缺乏根據個人當前狀態來做的判斷，即根據情緒判斷推薦音樂，而後者的問題則是測量所需的時間較長，無法達到即時測量的效果

## 整體流程圖
![](https://i.imgur.com/6YPynlC.png)

## Flutter 實做辨識 APP

### Quick start

```shell=
# (1) 先上 github clone repository
git clone https://github.com/liao2000/Emotion-Music-Player-AIoT-Project.git

# (2) 切換資料夾
cd Music-Player-AIoT-Project/

# (3) 連結手機，需要啟用 USB 偵錯

# (4) 直接運行程式
flutter run --release # release 優化版
flutter run           # debug 版本 (編譯比較快)

# (5) 或建置成 apk
flutter build apk
```

### 手刻

進入 Android studio 新增一個 flutter 套件

接著依序安裝以下套件

1. camera (處理相機)
2. tflite_flutter
3. image (處理圖片)
4. google_ml_kit (取得人臉)
5. http (發送 http 封包)
6. video_player (音樂播放器)
7. shared_preferences (類似 localstorage)

**lib/main.dart**

```dart=
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'pages/cameraPage.dart';
import 'pages/playerPage.dart';
import 'package:flutter/services.dart';

// main function like int main() in C
// Future means that main() is an asyn function

Future main() async {
  // Ensure that widgets are initialized
  WidgetsFlutterBinding.ensureInitialized();
  
  // get avalible camers
  final cameras = await availableCameras();

  // we use main camera for testing
  // so use cameras.first
  // i.e. camera[0]
  CameraDescription camera = cameras.first;
 
  // Set portraitUp
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])
      .then((_) {
      
    // call runApp()
    // the first param is an instance of Widget Class
    // this is a 習慣用法 in flutter
    runApp(MyApp(camera: camera));
  });
}

// There are two kinds of Widget in flutter
// One is Statelesswidget and the other one is Statefulwidget
// When we call setState()
// Only Statefulwidget could be rendered again.
class MyApp extends StatelessWidget {
  // (1) What is {}
  // {} means taht this an optional param
  // Besides, when you want to transfer this param
  // you need to specify their param name
  // for example:
  // int add({int a, int b}){
  //    return a+b
  // }
  // add(a: 3, b: 5)
  //
  // (2) What is required
  // when we add `required` before param
  // it means that this param is required
  // instead of 
  //
  // (3) like constructor in Java
  // class MyApp{
  //   MyApp(){
  //
  //   }
  // }
  //
  // (4) short hand
  // MyApp({required this.camera});
  // is equivalant to
  // MyApp({required camera}){
  //   this.camera = camera;
  // }
  
  MyApp({required this.camera});
  
  // all member in StatelessWidget must be final
  final CameraDescription camera;
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Emotion music player',
        theme: ThemeData(
          primarySwatch: Colors.cyan,
        ),
        home: InitialCamera(camera: camera));
  }
}

class InitialCamera extends StatefulWidget {
  InitialCamera({required this.camera});
  final CameraDescription camera;
  _InitialCameraState createState() => _InitialCameraState();
}

class _InitialCameraState extends State<InitialCamera> {

  // late 的用法是 dart2 的新特性
  // 代表 cameraCtrl 不可以是 null
  // 但是，我們一開始雖然不宣告的確是 null 
  // 但我們晚一點會給值
  // 在 dart2 裡
  // 如果有一個變數可以有 null 要在其型態前加入 ?
  // 比如 CameraController? cameraCtrl;
  
  late CameraController cameraCtrl;
  
  // initState 類似建構元
  // 但是在 setState() 是不會被呼叫
  // 只有第一次渲染時會呼叫
  
  @override
  void initState() {
    cameraCtrl = CameraController(widget.camera, ResolutionPreset.low);
    super.initState();
  }

  @override
  void dispose() {
    cameraCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
        future: cameraCtrl.initialize(),
        builder: (BuildContext context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Home(
              cameraCtrl,
              refresh: refresh,
            );
          } else if (snapshot.connectionState == ConnectionState.active) {
            return Center(child: CircularProgressIndicator());
          }

          // 效能比較差的手機可能離開畫面回來就卡了
          // 放一個重新整理方便使用
          return TextButton(
              onPressed: () {
                refresh();
              },
              child: Center(child: Text('重新整理')));
        });
  }

  void refresh() {
    if (mounted) {
      setState(() {});
    }
  }
}

class Home extends StatelessWidget {
  Home(this.cameraCtrl, {required this.refresh});
  
  // 再強調一下 statelessWidget 裡的成員都必需是 final
  final CameraController cameraCtrl;
  final Function refresh;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
        length: 2,
        child: Scaffold(
            appBar: AppBar(
              bottom: TabBar(
                tabs: [
                  Tab(icon: Icon(Icons.play_arrow, color: Colors.white)),
                  Tab(icon: Icon(Icons.camera_alt, color: Colors.white)),
                ],
              ),
              title: Text(
                "Emotion music player",
                style: TextStyle(color: Colors.white),
              ),
            ),
            body: TabBarView(
              children: [
                Player(cameraCtrl, refresh: refresh),
                MyCameraPreview(cameraCtrl, refresh: refresh),
              ],
            ),
            floatingActionButton: Ink(
                decoration: BoxDecoration(
                  color: Colors.cyan,
                  shape: BoxShape.circle,
                ),
                child: IconButton(
                  icon: Icon(Icons.favorite, color: Colors.white),
                  onPressed: () {
                    refresh();
                  },
                ))));
  }
}
```


**lib/box.dart**

自訂框出人臉的元件

```dart=
import 'package:flutter/material.dart';

class Box extends StatelessWidget {
  Box(
      {required this.x,
      required this.y,
      required this.width,
      required this.height,
      this.child,
      this.ratio = 1.0}); // screen width : photo width
      
  // dart 支援多個建構元
  // 如果要用一般的建構元
  // Box box1 = Box(...)
  // 如果要用另一種建構元
  // Box box2 = Box.square(...)

  Box.square(
      {required this.x,
      required this.y,
      required double side,
      this.child,
      this.ratio = 1.0})
      : width = side,
        height = side;

  final double x;
  final double y;
  final double width;
  final double height;
  final double ratio;
  final Widget? child;
  Widget build(BuildContext context) {
  
    // when we get the face range
    // we need to zoom the value
    // use `ratio` for zooming
    return Positioned(
        left: x * ratio,
        top: y * ratio,
        width: width * ratio,
        height: height * ratio,
        // Stack is a Widget that can
        // render Widget on z-axis
        child: Stack(clipBehavior: Clip.none, children: [
          Container(
              decoration: BoxDecoration(
            border: Border.all(
              color: Colors.cyan,
              width: 3,
            ),
          )),
          // this is a short hand
          // if(child == null){
          //     Container()
          // }else{
          //     child
          // }
          // same usage in PHP7
          child ?? Container()
        ]));
  }
}
```

**lib/classifer.dart**

分類器

```dart=
import 'package:tflite_flutter/tflite_flutter.dart';

class Classifier {
  var _inputShape;
  var _outputShape;
  var _interpreter;
  var _outputSize = 1;

  dynamic get inputShape => _inputShape;
  dynamic get outputShape => _outputShape;
  dynamic get interpreter => _interpreter;
  dynamic get outputSize => _outputSize;

  Future<Interpreter> loadModel(String path) async {
    try {
      if (_interpreter != null) return _interpreter;
      _interpreter = await Interpreter.fromAsset(path);
      _inputShape = _interpreter.getInputTensor(0).shape;
      _outputShape = _interpreter.getOutputTensor(0).shape;

      _outputShape.forEach((e) {
        _outputSize *= e as int;
      });

      return _interpreter;
    } catch (e) {
      throw ('Unable to create interpreter, Caught Exception: $e');
    }
  }

  int run(input) {
    var output = List.filled(_outputSize, 0).reshape(_outputShape);
    _interpreter.run(input, output);
    return _max(output[0]);
  }

  int _max(List<num> list) {
    if (list == null || list.length == 0) {
      throw ("List is empty");
    }
    int index = 0;
    for (int i = 0; i < list.length; i++) {
      if (list[i] > list[index]) {
        index = i;
      }
    }
    return index;
  }
}
```

**lib/imageConvert.dart**

圖片套件轉換，抓別人寫好的來改

```dart=
/*
* Reference FROM
* https://github.com/am15h/object_detection_flutter/blob/master/lib/utils/image_utils.dart
*/
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as imageLib;

/// ImageUtils
class ImageUtils {
  /// Converts a [CameraImage] in YUV420 format to [imageLib.Image] in RGB format
  static imageLib.Image convertCameraImage(CameraImage cameraImage) {
    if (cameraImage.format.group == ImageFormatGroup.yuv420) {
      return convertYUV420ToImage(cameraImage);
    } else if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
      return convertBGRA8888ToImage(cameraImage);
    }
    throw ("Format not support");
  }

  /// Converts a [CameraImage] in BGRA888 format to [imageLib.Image] in RGB format
  static imageLib.Image convertBGRA8888ToImage(CameraImage cameraImage) {
    imageLib.Image img = imageLib.Image.fromBytes(cameraImage.planes[0].width!,
        cameraImage.planes[0].height!, cameraImage.planes[0].bytes,
        format: imageLib.Format.bgra);
    return img;
  }

  /// Converts a [CameraImage] in YUV420 format to [imageLib.Image] in RGB format
  static imageLib.Image convertYUV420ToImage(CameraImage cameraImage) {
    final int width = cameraImage.width;
    final int height = cameraImage.height;

    final int uvRowStride = cameraImage.planes[1].bytesPerRow;
    final int uvPixelStride = cameraImage.planes[1].bytesPerPixel!;

    final image = imageLib.Image(width, height);

    for (int w = 0; w < width; w++) {
      for (int h = 0; h < height; h++) {
        final int uvIndex =
            uvPixelStride * (w / 2).floor() + uvRowStride * (h / 2).floor();
        final int index = h * width + w;

        final y = cameraImage.planes[0].bytes[index];
        final u = cameraImage.planes[1].bytes[uvIndex];
        final v = cameraImage.planes[2].bytes[uvIndex];

        image.data[index] = ImageUtils.yuv2rgb(y, u, v);
      }
    }
    return image;
  }

  /// Convert a single YUV pixel to RGB
  static int yuv2rgb(int y, int u, int v) {
    // Convert yuv pixel to rgb
    int r = (y + v * 1436 / 1024 - 179).round();
    int g = (y - u * 46549 / 131072 + 44 - v * 93604 / 131072 + 91).round();
    int b = (y + u * 1814 / 1024 - 227).round();

    // Clipping RGB values to be inside boundaries [ 0 , 255 ]
    r = r.clamp(0, 255);
    g = g.clamp(0, 255);
    b = b.clamp(0, 255);

    return 0xff000000 |
        ((b << 16) & 0xff0000) |
        ((g << 8) & 0xff00) |
        (r & 0xff);
  }
}
```

**lib/player.dart**

自訂音樂播放器元件

```dart=
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart' as vp;
import 'dart:async';

// 把 video_player 再包裝讓他更好用
class VideoPlayer extends StatefulWidget {
  VideoPlayer(this.videoPath,
      {this.child,
      this.video = true,
      this.autoPlay = false,
      this.onEnd,
      this.onError});
  final String videoPath;
  final bool autoPlay, video;
  final Widget? child;
  final Function? onEnd;
  final Function? onError;
  @override
  _VideoPlayerState createState() => _VideoPlayerState();
}

class _VideoPlayerState extends State<VideoPlayer> {
  // 之前提過了 late 就是指我晚點填值，所以 _controller 不可能是 null
  late vp.VideoPlayerController _controller;
  // Duration? 代表 _duration, _position 可以是 null，這是照套件用的
  Duration? _duration, _position;
  // 這幾個 boolean falg 就照他字面的意思
  bool _isPlaying = false, _isEnd = false;
  String oldPath = '';

  vp.VideoPlayerController initController() {
    vp.VideoPlayerController _newController =
        vp.VideoPlayerController.network("${widget.videoPath}");
    _newController.addListener(() {
      if (_newController.value.hasError) {
        if (mounted) {
          if (widget.onError != null) {
            widget.onError!();
            print(_newController.value.errorDescription);
          }
          setState(() {});
        }
      }

      if (_newController.value.isInitialized) {
        final bool isPlaying = _newController.value.isPlaying;
        if (isPlaying != _isPlaying) {
          setState(() {
            _isPlaying = isPlaying;
          });
        }

        setState(() {
          _duration = _newController.value.duration;
        });

        Timer.run(() {
          setState(() {
            _position = _newController.value.position;
            if (_position != null) {
              if (_duration?.compareTo(_position!) == 0 ||
                  _duration?.compareTo(_position!) == -1) {
                if (widget.onEnd != null) {
                  _isEnd = true;
                  widget.onEnd!();
                }
              } else {
                _isEnd = false;
              }
            }
          });
        });
      }
    });

    _newController.initialize().then((_) {
      oldPath = widget.videoPath;
      // Ensure the first frame is shown after the video is initialized,
      // even before the play button has been pressed.
      if (mounted) {
        if (widget.autoPlay) {
          _newController.seekTo(Duration(seconds: 0));
          _newController.play();
        } else {}
        setState(() {});
      }
    });

    return _newController;
  }

  void initState() {
    super.initState();
    _controller = initController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void reInitialize() async {
    if (_controller.value.isInitialized) {
      await _controller.dispose();
    }
    _controller = initController();
  }

  @override
  Widget build(BuildContext context) {
    // This is very important
    // If the new song url is not euqal to origmal one
    // We need to reintialize the video controller
    // Because video controller cannot change
    // media resource directly
    // 就一個坑啦，研究很久
    if (widget.videoPath != oldPath) {
      print("Controller update new url: ${widget.videoPath}");
      if (_controller != null && _controller.value.isInitialized) {
        reInitialize();
      }
    }

    if (_controller.value.hasError) {
      return Icon(Icons.error);
    } else if (_controller.value.isInitialized) {
      return ConstrainedBox(
          constraints: BoxConstraints(maxWidth: 640, minWidth: 250),
          child: Column(children: [
            (widget.video)
                ? AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: vp.VideoPlayer(_controller),
                  )
                : Container(),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              IconButton(
                icon: _controller.value.isPlaying && !_isEnd
                    ? Icon(Icons.pause)
                    : Icon(Icons.play_arrow),
                iconSize: 18.0,
                onPressed: () {
                  setState(() {
                    if (_controller.value.isPlaying) {
                      _controller.pause();
                    } else {
                      // if is end, replay
                      if (_isEnd) {
                        _controller.seekTo(Duration(seconds: 0));
                      }
                      _controller.play();
                    }
                  });
                },
              ),
              SizedBox(width: 10),
              // From more info about videoProgressIndicator
              // Head on: https://pub.dev/documentation/video_player/latest/video_player/VideoProgressIndicator-class.html
              Expanded(
                child: MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: vp.VideoProgressIndicator(_controller,
                        colors: vp.VideoProgressColors(
                          playedColor: Colors.lightGreen,
                          bufferedColor: Colors.lightGreen[100]!,
                          backgroundColor: Colors.grey[300]!,
                        ),
                        allowScrubbing: true)),
              ),
              SizedBox(width: 10),
              Text(
                  '${durationFormatter(_position)} / ${durationFormatter(_duration)}'),
              SizedBox(width: 10),
              widget.child ?? SizedBox(),
            ])
          ]));
    } else {
      return Center(
          child: Padding(
              padding: EdgeInsets.symmetric(vertical: 15),
              child: CircularProgressIndicator()));
    }
  }
}

String durationFormatter(Duration? d) {
  if (d == null) return "";
  return (d.inHours == 0)
      ? "${d.inMinutes.remainder(60).toString().padLeft(2, "0")}:${(d.inSeconds.remainder(60)).toString().padLeft(2, "0")}"
      : "${d.inHours.toString().padLeft(2, "0")}:${d.inMinutes.remainder(60).toString().padLeft(2, "0")}:${(d.inSeconds.remainder(60)).toString().padLeft(2, "0")}";
}
```

**lib/preprocessing.dart**

將圖片做預處理的套件

```dart=
import 'package:image/image.dart' as img;
import 'package:camera/camera.dart';

// 3D List
class ImagePrehandle {
  static List<List<List<double>>> uint32ListToRGB3D(img.Image src) {
    int k = 0;
    int e;
    List<List<List<double>>> rgb = [];
    for (int i = 0; i < src.width; i++) {
      List<List<double>> row = [];
      for (int j = 0; j < src.height; j++) {
        // e is ##AABBGGRR
        e = src.data[k++];
        row.add([
          (e & 255) / 255.0,
          ((e >> 8) & 255) / 255.0,
          ((e >> 16) & 255) / 255.0
        ]);
      }
      rgb.add(row);
    }
    return rgb;
  }

  static img.Image convertYUV420(CameraImage image) {
    var ret = img.Image(image.width, image.height); // Create Image buffer

    Plane plane = image.planes[0];
    const int shift = (0xFF << 24);

    // Fill image buffer with plane[0] from YUV420_888
    for (int x = 0; x < image.width; x++) {
      for (int planeOffset = 0;
          planeOffset < image.height * image.width;
          planeOffset += image.width) {
        final pixelColor = plane.bytes[planeOffset + x];
        // color: 0x FF  FF  FF  FF
        //           A   B   G   R
        // Calculate pixel color
        var newVal =
            shift | (pixelColor << 16) | (pixelColor << 8) | pixelColor;

        ret.data[planeOffset + x] = newVal;
      }
    }

    return ret;
  }
}
```

**接著實作兩個 page 頁面**

**lib/pages/playerPage.dart**

main page，會抓臉再推播音樂

```dart=
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_ml_kit/google_ml_kit.dart';
import 'package:image/image.dart' as img;
import "dart:async";
import "dart:convert" as convert;
import '../classifier.dart';
import '../imageConvert.dart';
import '../preprocessing.dart';
import '../player.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// model label
// '驚喜', '害怕', '噁心', '開心', '傷心', '生氣', '無'
// music server label
// 1, 0, 3, 1, 2, 3, 4
const facialModel = 'fe93.tflite';
const facialLabel = [1, 0, 3, 1, 2, 3, 4];
const musicServerLabel = ['害怕', '開心', '難過', '生氣', '無表情'];
const noFace = 4;

// 這個是測試用的歌 CHiCO 唱的，好聽
const presetMusicName = 'カヌレ';
const presetMusicPath = 'https://had.name/data/daily-music/aud/ENq3c.mp3';

class Player extends StatefulWidget {
  Player(this.cameraCtrl, {this.refresh});
  final CameraController cameraCtrl;
  final Function? refresh;
  @override
  _PlayerState createState() => _PlayerState();
}

class _PlayerState extends State<Player> {
  late FaceDetector faceDetector;
  String emotion = '';
  String musicName = '';
  String musicPath = '';
  bool autoPlay = false; // preset is false
  bool loadLastMusic = false;

  // 使用者載入程式時，會先推播上次聽的歌
  // 注意：這個在 debug mode 沒辦法使用
  // 但 release mode 可以
  void loadPreference() async {
    print("call loadPreference()");
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      musicName = prefs.getString('musicName') ?? presetMusicName;
      musicPath = prefs.getString('musicPath') ?? presetMusicPath;
      // Success get last music info
      if (mounted) {
        setState(() {
          loadLastMusic = true;
        });
      }
    } catch (e) {
      // cannot get last music info but can get random music info
      loadLastMusic = true;
      getMusic(noFace);
    }
  }

  @override
  void initState() {
    super.initState();
    
    // 載入 google ml kit 套件做臉部偵測
    faceDetector = GoogleMlKit.vision.faceDetector(FaceDetectorOptions());
    loadPreference();
  }

  @override
  void dispose() {
    faceDetector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      SizedBox(height: 15),
      Padding(
          padding: EdgeInsets.all(20),
          child: Text(
            (loadLastMusic) ? musicName : "載入中...",
            style: TextStyle(fontSize: 18),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          )),
      Padding(
          padding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
          child: (loadLastMusic)
              ? VideoPlayer(
                  musicPath,
                  autoPlay: autoPlay,
                  video: false,
                  onEnd: () {
                    _detect();
                  },
                  onError: () {
                    snackBar("音樂網址錯誤！瑋哥快去修！", context);
                  },
                )
              : CircularProgressIndicator()),
      Padding(
        padding: EdgeInsets.symmetric(vertical: 20),
        child: Text('$emotion'),
      ),
      (widget.cameraCtrl.value.isStreamingImages)
          ? IconButton(
              iconSize: 50,
              icon: Icon(Icons.stop, color: Colors.black),
              onPressed: () async {
                await _stopDetect([]);
                setState(() {});
              },
            )
          : IconButton(
              iconSize: 50,
              icon: Icon(Icons.face, color: Colors.black),
              onPressed: () async {
                if (mounted) _detect();
              },
            ),
    ]);
  }

  // give each label's number
  Future _stopDetect(score) async {
    if (widget.cameraCtrl.value.isStreamingImages) {
      await widget.cameraCtrl.stopImageStream();
      if (score.length > 0) {
        print(score);
        int maxLabel = 0;
        for (var i = 1; i < score.length; i++) {
          if (score[i] > score[maxLabel]) {
            maxLabel = i;
          }
        }
        print("$maxLabel");
        // delay 3 seconds for waiting the remainder of labels return
        Timer(Duration(milliseconds: 2500), () {
          setState(() {
            if (maxLabel == noFace) {
              emotion = "沒有偵測到您的表情，為您隨機點播";
            } else {
              emotion = "正在為您推薦「${musicServerLabel[maxLabel]}」適合聽的歌";
            }
          });
        });

        await getMusic(maxLabel);
      }
    }
  }

  Future _detect() async {
    bool lock = false;
    Classifier cls = Classifier();
    try {
      await cls.loadModel(facialModel);
    } catch (e) {
      print(e);
    }

    // the numbers of each label
    List score = [0, 0, 0, 0, 0]; // 0 - 4
    try {
      // timeout
      // try to predict in 5 seconds
      Timer(Duration(seconds: 5), () {
        if (widget.cameraCtrl.value.isStreamingImages) {
          print("5秒到了");
          _stopDetect(score);
        }
      });

      widget.cameraCtrl.startImageStream((CameraImage cameraImg) async {
        // 用 lock 鎖互斥鎖
        // 可能會有線程不安全，但發生率很低目前沒遇到
        // 可能要再研究一下正確的用法
        if (!lock) {
          lock = true;
          final WriteBuffer allBytes = WriteBuffer();
          for (Plane plane in cameraImg.planes) {
            allBytes.putUint8List(plane.bytes);
          }
          final InputImage visionImage = InputImage.fromBytes(
              bytes: allBytes.done().buffer.asUint8List(),
              inputImageData: InputImageData(
                  size: Size(
                      cameraImg.width.toDouble(), cameraImg.height.toDouble()),
                  imageRotation: InputImageRotation.Rotation_90deg));
          final List<Face> faces = await faceDetector.processImage(visionImage);

          img.Image convertedImg = ImageUtils.convertCameraImage(cameraImg);
          img.Image rotationImg = img.copyRotate(convertedImg, 90);

          if (faces.length == 0) {
            setState(() {
              emotion = musicServerLabel[noFace];
              score[noFace] += 1;
            });
          }

          for (Face face in faces) {
          // 取得所有圖片流中的人臉
          final List<Face> faces = await faceDetector.processImage(visionImage);

            final Rect boundingBox = face.boundingBox;
            double faceRange = boundingBox.bottom - boundingBox.top;

            if (cls.interpreter != null) {
              img.Image croppedImage = img.copyCrop(
                  rotationImg,
                  boundingBox.left.toInt(),
                  boundingBox.top.toInt(),
                  faceRange.toInt(),
                  faceRange.toInt());

              img.Image resultImage = img.copyResize(croppedImage,
                  width: cls.inputShape[1], height: cls.inputShape[2]);

              // 進分類器做分類
              var input = ImagePrehandle.uint32ListToRGB3D(resultImage);
              var output = cls.run([input]);
              print(facialLabel[output]);
              
              // 渲染
              setState(() {
                score[facialLabel[output]] += 1;
                emotion = musicServerLabel[facialLabel[output]];
              });
            } else {
              print("interpreter is null");
            }
          }
          lock = false;
        }
      });
    } catch (e) {
      widget.refresh!();
      snackBar('$e', context);
    }
  }

  // 透過 http 套件發送封包給後台伺服器
  // 類似網頁的 Ajax
  Future getMusic(int label) async {
    var url = Uri.parse(
        'https://listen-with-emotion.herokuapp.com/predict?label=$label');
    var res = await http.get(url);
    if (res.statusCode == 200) {
      try {
        Map data = convert.jsonDecode(res.body);
        print(data);
        setState(() {
          musicName = data["filename"];
          musicPath = data["url"];
          autoPlay = true;
        });
      } catch (e) {
        setState(() {
          musicName = presetMusicName;
          musicPath = presetMusicPath;
          autoPlay = false;
        });
        snackBar('伺服器錯誤', context);
      }
      // save music
      try {
        SharedPreferences prefs = await SharedPreferences.getInstance();
        prefs.setString("musicName", musicName);
        prefs.setString("musicPath", musicPath);
      } catch (e) {
        print("無法儲存該筆記錄");
      }
    } else {
      snackBar('網路錯誤 ${res.statusCode}', context);
    }
  }
}


// 把 snackbar 包裝
// scakbar 就是螢幕會從下面噴黑色一條的東東
// 另一種常見的叫 toastBar
// 就是一樣螢幕下但是是灰灰的一塊

void snackBar(String msg, BuildContext context) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      action: SnackBarAction(
          label: 'close',
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          })));
}
```


**lib/pages/cameraPage.dart**

camera page 是拿來測試用的，測試鏡頭下是否有抓到表情

```dart=
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_ml_kit/google_ml_kit.dart';
import 'package:image/image.dart' as img;
import '../classifier.dart';
import '../imageConvert.dart';
import '../preprocessing.dart';
import '../box.dart';

// 我們的模型位於 assets/fe93.tflite
// python tensorflow 有套件可以把 h5 模型轉換成 tflite
// 要注意這個轉換是不可逆的
// 所以原模型還是要留著

const facialModel = 'fe93.tflite';
const facialLabel = ['驚喜', '害怕', '噁心', '開心', '傷心', '生氣', '無'];

class MyCameraPreview extends StatefulWidget {
  MyCameraPreview(this.cameraCtrl, {this.refresh});
  final CameraController cameraCtrl;
  final Function? refresh;
  @override
  _MyCameraPreviewState createState() => _MyCameraPreviewState();
}

class _MyCameraPreviewState extends State<MyCameraPreview> {
  late FaceDetector faceDetector;
  List<Widget> boxList = [];

  @override
  void initState() {
    super.initState();
    faceDetector = GoogleMlKit.vision.faceDetector(FaceDetectorOptions());
  }

  @override
  void dispose() {
    faceDetector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> children = [
      CameraPreview(widget.cameraCtrl),
      Align(
          alignment: Alignment.bottomCenter,
          child: Padding(
              padding: EdgeInsets.all(10),
              child: Ink(
                  decoration: BoxDecoration(
                    color: Colors.cyan,
                    shape: BoxShape.circle,
                  ),
                  child: (widget.cameraCtrl.value.isStreamingImages)
                      ? IconButton(
                          icon: Icon(Icons.stop, color: Colors.white, size: 30),
                          onPressed: () async {
                            await _stopDetect();
                            setState(() {});
                          },
                        )
                      : IconButton(
                          icon: Icon(Icons.radio_button_checked,
                              color: Colors.white, size: 30),
                          onPressed: () async {
                            if (mounted) _detect();
                          },
                        )))),
    ];
    children.addAll(boxList);

    return Stack(children: children);
  }

  Future _stopDetect() async {
    if (widget.cameraCtrl.value.isStreamingImages) {
      await widget.cameraCtrl.stopImageStream();
      widget.refresh!();
    }
  }

  Future _detect() async {
    bool lock = false;
    Classifier cls = Classifier();
    try {
      await cls.loadModel(facialModel);
    } catch (e) {
      print(e);
    }

    // 載入 image stream
    try {
      widget.cameraCtrl.startImageStream((CameraImage cameraImg) async {
        setState(() {});
        if (!lock) {
          lock = true;
          final WriteBuffer allBytes = WriteBuffer();
          for (Plane plane in cameraImg.planes) {
            allBytes.putUint8List(plane.bytes);
          }
          // 透過剛剛介紹的圖片轉換套件轉換格式
          final InputImage visionImage = InputImage.fromBytes(
              bytes: allBytes.done().buffer.asUint8List(),
              inputImageData: InputImageData(
                  size: Size(
                      cameraImg.width.toDouble(), cameraImg.height.toDouble()),
                  imageRotation: InputImageRotation.Rotation_90deg));
        
          final List<Face> faces = await faceDetector.processImage(visionImage);

          img.Image convertedImg = ImageUtils.convertCameraImage(cameraImg);
          img.Image rotationImg = img.copyRotate(convertedImg, 90);

          boxList = [];
          for (Face face in faces) {
            final Rect boundingBox = face.boundingBox;
            double faceRange = boundingBox.bottom - boundingBox.top;

            if (cls.interpreter != null) {
              // 剪下臉部的範圍
              img.Image croppedImage = img.copyCrop(
                  rotationImg,
                  boundingBox.left.toInt(),
                  boundingBox.top.toInt(),
                  faceRange.toInt(),
                  faceRange.toInt());
                  
              // 縮放成模型大小 100*100
              img.Image resultImage = img.copyResize(croppedImage,
                  width: cls.inputShape[1], height: cls.inputShape[2]);

              // 進分類器分類
              var input = ImagePrehandle.uint32ListToRGB3D(resultImage);
              var output = cls.run([input]);
              print(facialLabel[output]);

              // 將臉部範圍圈選並渲染
              boxList.add(Box.square(
                  x: boundingBox.left,
                  y: boundingBox.top,
                  side: boundingBox.bottom - boundingBox.top,
                  ratio: MediaQuery.of(context).size.width / cameraImg.height,
                  child: Positioned(
                      top: -25,
                      left: 0,
                      child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text("${facialLabel[output]}",
                                style: TextStyle(
                                    fontSize: 18,
                                    color: Colors.white,
                                    backgroundColor: Colors.cyan))
                          ]))));
            } else {
              print("interpreter is null");
            }
          }
          lock = false;
        }
      });
    } on CameraException catch (e) {
      print("----------------------------------------");
      if (widget.refresh != null) {
        widget.refresh!();
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('$e'),
          action: SnackBarAction(
              label: 'close',
              onPressed: () {
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
              })));
    }
  }
}
```

## 後端

### 根據音樂生成曲風

使用LSTM模型生成，將資料集轉換為四個音樂特徵，約每3秒截取一個特徵。
音樂分析使用librosa，提取mfcc, chroma, spatial contrast, spatial centroid
```python=
import librosa
import math
import os

import numpy as np


class GenreFeatureData:

    "Music audio features for genre classification"
    hop_length = None
    genre_list = [
        "blues",
        "classical",
        "country",
        "disco",
        "hiphop",
        "metal",
        "pop",
        "reggae",
        "rock",
    ]

    dir_trainfolder = "./gtzan/_train"
    dir_devfolder = "./gtzan/_validation"
    dir_testfolder = "./gtzan/_test"
    dir_all_files = "./gtzan"

    train_X_preprocessed_data = "./gtzan/data_train_input.npy"
    train_Y_preprocessed_data = "./gtzan/data_train_target.npy"
    dev_X_preprocessed_data = "./gtzan/data_validation_input.npy"
    dev_Y_preprocessed_data = "./gtzan/data_validation_target.npy"
    test_X_preprocessed_data = "./gtzan/data_test_input.npy"
    test_Y_preprocessed_data = "./gtzan/data_test_target.npy"

    train_X = train_Y = None
    dev_X = dev_Y = None
    test_X = test_Y = None

    def __init__(self):
        self.hop_length = 512

        self.timeseries_length_list = []
        self.trainfiles_list = self.path_to_audiofiles(self.dir_trainfolder)
        self.devfiles_list = self.path_to_audiofiles(self.dir_devfolder)
        self.testfiles_list = self.path_to_audiofiles(self.dir_testfolder)

        self.all_files_list = []
        self.all_files_list.extend(self.trainfiles_list)
        self.all_files_list.extend(self.devfiles_list)
        self.all_files_list.extend(self.testfiles_list)

        # compute minimum timeseries length, slow to compute, caching pre-computed value of 1290
        # self.precompute_min_timeseries_len()
        # print("min(self.timeseries_length_list) ==" + str(min(self.timeseries_length_list)))
        # self.timeseries_length = min(self.timeseries_length_list)

        self.timeseries_length = (
            128
        )   # sequence length == 128, default fftsize == 2048 & hop == 512 @ SR of 22050
        #  equals 128 overlapped windows that cover approx ~3.065 seconds of audio, which is a bit small!

    def load_preprocess_data(self):
        print("[DEBUG] total number of files: " + str(len(self.timeseries_length_list)))

        # Training set
        self.train_X, self.train_Y = self.extract_audio_features(self.trainfiles_list)
        with open(self.train_X_preprocessed_data, "wb") as f:
            np.save(f, self.train_X)
        with open(self.train_Y_preprocessed_data, "wb") as f:
            self.train_Y = self.one_hot(self.train_Y)
            np.save(f, self.train_Y)

        # Validation set
        self.dev_X, self.dev_Y = self.extract_audio_features(self.devfiles_list)
        with open(self.dev_X_preprocessed_data, "wb") as f:
            np.save(f, self.dev_X)
        with open(self.dev_Y_preprocessed_data, "wb") as f:
            self.dev_Y = self.one_hot(self.dev_Y)
            np.save(f, self.dev_Y)

        # Test set
        self.test_X, self.test_Y = self.extract_audio_features(self.testfiles_list)
        with open(self.test_X_preprocessed_data, "wb") as f:
            np.save(f, self.test_X)
        with open(self.test_Y_preprocessed_data, "wb") as f:
            self.test_Y = self.one_hot(self.test_Y)
            np.save(f, self.test_Y)

    def load_deserialize_data(self):

        self.train_X = np.load(self.train_X_preprocessed_data)
        self.train_Y = np.load(self.train_Y_preprocessed_data)

        self.dev_X = np.load(self.dev_X_preprocessed_data)
        self.dev_Y = np.load(self.dev_Y_preprocessed_data)

        self.test_X = np.load(self.test_X_preprocessed_data)
        self.test_Y = np.load(self.test_Y_preprocessed_data)

    def precompute_min_timeseries_len(self):
        for file in self.all_files_list:
            print("Loading " + str(file))
            y, sr = librosa.load(file)
            self.timeseries_length_list.append(math.ceil(len(y) / self.hop_length))

    def extract_audio_features(self, list_of_audiofiles):

        data = np.zeros(
            (len(list_of_audiofiles), self.timeseries_length, 33), dtype=np.float64
        )
        target = []

        for i, file in enumerate(list_of_audiofiles):
            y, sr = librosa.load(file)
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, hop_length=self.hop_length, n_mfcc=13
            )
            spectral_center = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=self.hop_length
            )
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
            spectral_contrast = librosa.feature.spectral_contrast(
                y=y, sr=sr, hop_length=self.hop_length
            )
            splits = file.split('.')
            genre = splits[1].split('/')[-1]
            print(f'genre is {genre}')
            target.append(genre)

            data[i, :, 0:13] = mfcc.T[0:self.timeseries_length, :]
            data[i, :, 13:14] = spectral_center.T[0:self.timeseries_length, :]
            data[i, :, 14:26] = chroma.T[0:self.timeseries_length, :]
            data[i, :, 26:33] = spectral_contrast.T[0:self.timeseries_length, :]

            print(
                "Extracted features audio track %i of %i."
                % (i + 1, len(list_of_audiofiles))
            )

        return data, target

    def one_hot(self, Y_genre_strings):
        y_one_hot = np.zeros((len(Y_genre_strings), len(self.genre_list)))
        for i, genre_string in enumerate(Y_genre_strings):
            index = self.genre_list.index(genre_string)
            y_one_hot[i, index] = 1
        return y_one_hot

    @staticmethod
    def path_to_audiofiles(dir_folder):
        list_of_audio = []
        for file in os.listdir(dir_folder):
            if file.endswith(".wav"):
                directory = "%s/%s" % (dir_folder, file)
                list_of_audio.append(directory)
        return list_of_audio
```

上述特徵作為x值，曲風作為y值，訓練類神經網路

```python=
model = Sequential()

model.add(LSTM(units=128, dropout=0.05, recurrent_dropout=0.35, return_sequences=True, input_shape=input_shape))
model.add(LSTM(units=32,  dropout=0.05, recurrent_dropout=0.35, return_sequences=False))
model.add(Dense(units=genre_features.train_Y.shape[1], activation="softmax"))

model.compile(loss="categorical_crossentropy", optimizer=Adam(learning_rate=1e-5), metrics=["accuracy"])
```

### 轉換輸入情緒到曲風

1. 先分析音樂庫各歌曲的曲風
2. 先假定情緒對各曲風機率均等，人工選擇適合聽的類型，修改原有機率分布
3. 依照機率選擇該情緒對映的曲風（隨機分布）
4. 於歌曲庫選擇一個該曲風的音樂
5. 利用flask傳回到前端APP
6. 依據使用者回饋再次更新機率分布(TODO)

完整程式碼於app.py和src/predict.py

## 結語

雖然目前系統還是以純APP的方式實現，但未來應可結合帶有鏡頭的微處理器做即時分析，並於手機APP上可以播放音樂，也可直接用手機連結到車用電腦播放。

## Reference

* [EMOTION-BASED MUSIC RECOMMENDATION SYSTEM USING A DEEP REINFORCEMENT LEARNING APPROACH](https://medium.com/analytics-vidhya/emotion-based-music-recommendation-system-using-a-deep-reinforcement-learning-approach-6d23a24d3044)
* [ruohoruotsi /LSTM-Music-Genre-Classification ](https://github.com/ruohoruotsi/LSTM-Music-Genre-Classification/)

