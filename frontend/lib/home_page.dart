import 'dart:typed_data';
import 'dart:html' as html;

import 'package:style_transfer/home_model.dart';
import 'package:style_transfer/widgets/widgets.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class HomePage extends StatelessWidget {
  HomePage({super.key});

  final formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: <Widget>[
          const SliverAppBar(
            title: Text('Style Transfer'),
            pinned: false,
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            sliver: SliverToBoxAdapter(
              child: Row(
                children: <Widget>[
                  _SelectImagesColumn(formKey),
                  const SizedBox(width: 40),
                  _ResultImageColumn(formKey),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SelectImagesColumn extends StatefulWidget {
  final GlobalKey<FormState> formKey;

  const _SelectImagesColumn(this.formKey);

  @override
  State<_SelectImagesColumn> createState() => _SelectImagesColumnState();
}

class _SelectImagesColumnState extends State<_SelectImagesColumn> {
  var inProgress = false;

  Future<Uint8List?> pickFile() async {
    var result = await FilePicker.platform.pickFiles(type: FileType.image);
    return result?.files.first.bytes;
  }

  void downloadImage(Uint8List bytes, String filename,
      {String extension = 'png'}) {
    final blob = html.Blob([bytes]);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.document.createElement('a') as html.AnchorElement
      ..href = url
      ..style.display = 'none'
      ..download = '$filename.$extension';
    html.document.body!.children.add(anchor);

    anchor.click();

    html.document.body!.children.remove(anchor);
    html.Url.revokeObjectUrl(url);
  }

  @override
  Widget build(BuildContext context) {
    var model = context.read<HomeModel>();
    var submit = context.watch<HomeModel>().content != null &&
        context.watch<HomeModel>().style != null;
    var result = context.watch<HomeModel>().result;
    return Column(
      children: <Widget>[
        const Text(
          'Content',
          style: TextStyle(fontSize: 15),
        ),
        ImageStub(
          imageBytes: context.watch<HomeModel>().content,
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () async {
            var res = await pickFile();
            // model.content = res;
            model.setContent(res, (width, height) {
              showDialog(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: const Text('Too high resolution'),
                    content:
                        Text('Your image resolution was set to ${width}x$height'),
                    actions: <Widget>[
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pop();
                        },
                        child: const Text('Close'),
                      ),
                    ],
                  );
                },
              );
            });
          },
          child: const Text('Choose image'),
        ),
        const SizedBox(height: 30),
        const Text(
          'Style',
          style: TextStyle(fontSize: 15),
        ),
        ImageStub(
          imageBytes: context.watch<HomeModel>().style,
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () async {
            var res = await pickFile();
            model.style = res;
          },
          child: const Text('Choose image'),
        ),
        const SizedBox(height: 50),
        inProgress
            ? const CircularProgressIndicator()
            : FilledButton(
                onPressed: submit
                    ? () async {
                        setState(() {
                          inProgress = true;
                        });
                        await model.submit();
                        setState(() {
                          inProgress = false;
                        });
                      }
                    : null,
                child: const Text('Submit'),
              ),
        const SizedBox(height: 30),
        FilledButton(
          onPressed: result != null
              ? () {
                  downloadImage(result, 'result');
                }
              : null,
          child: const Text('Download'),
        ),
      ],
    );
  }
}

class _ResultImageColumn extends StatelessWidget {
  const _ResultImageColumn(this.formKey);

  final GlobalKey<FormState> formKey;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        // mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Text(
            'Result',
            style: TextStyle(
              fontSize: Theme.of(context).textTheme.headlineMedium?.fontSize,
            ),
          ),
          const SizedBox(height: 20),
          ImageStub(
            height: 500,
            width: 888,
            text: 'Submit your images to get the result',
            imageBytes: context.watch<HomeModel>().result,
          ),
          const SizedBox(height: 20),
          Text(
            'Control panel',
            style: TextStyle(
              fontSize: Theme.of(context).textTheme.headlineSmall?.fontSize,
            ),
          ),
          const SizedBox(height: 10),
          _ControlPanel(formKey),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}

class _ControlPanel extends StatelessWidget {
  const _ControlPanel(this.formKey);

  final GlobalKey<FormState> formKey;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: <Widget>[
        _SizeSelectors(formKey),
        _Sliders(),
      ],
    );
  }
}

class _SizeSelectors extends StatelessWidget {
  const _SizeSelectors(this.formKey);

  final GlobalKey<FormState> formKey;
  @override
  Widget build(BuildContext context) {
    var model = context.read<HomeModel>();
    return ConstrainedBox(
      constraints: const BoxConstraints(
        maxWidth: 150,
      ),
      child: Form(
        key: formKey,
        child: Column(
          children: <Widget>[
            TextFormField(
              controller: model.widthController,
              decoration: const InputDecoration(
                labelText: 'Width',
                border: OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.next,
              validator: (value) {
                if (value == null) return null;
                try {
                  int res = int.parse(value);
                  if (res < 256 || res > 1920) {
                    return 'from 256 to 1920';
                  }
                  return null;
                } catch (_) {
                  return 'Invalid number';
                }
              },
              onChanged: (value) {
                if (formKey.currentState != null &&
                    formKey.currentState!.validate()) {
                  context.read<HomeModel>().width = int.parse(value);
                }
              },
            ),
            const SizedBox(height: 10),
            TextFormField(
              controller: model.heightController,
              decoration: const InputDecoration(
                labelText: 'Height',
                border: OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.next,
              validator: (value) {
                if (value == null) return null;
                try {
                  int res = int.parse(value);
                  if (res < 256 || res > 1080) {
                    return 'from 256 to 1080';
                  }
                  return null;
                } catch (_) {
                  return 'Invalid number';
                }
              },
              onChanged: (value) {
                if (formKey.currentState != null &&
                    formKey.currentState!.validate()) {
                  context.read<HomeModel>().height = int.parse(value);
                }
              },
            ),
            const SizedBox(height: 10),
            TextFormField(
              controller: model.epochsController,
              decoration: const InputDecoration(
                labelText: 'Epochs',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null) return null;
                try {
                  int res = int.parse(value);
                  if (res < 1 || res > 5000) {
                    return 'from 1 to 5000';
                  }
                  return null;
                } catch (_) {
                  return 'Invalid number';
                }
              },
              onChanged: (value) {
                if (formKey.currentState != null &&
                    formKey.currentState!.validate()) {
                  context.read<HomeModel>().epochs = int.parse(value);
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _Sliders extends StatefulWidget {
  @override
  State<_Sliders> createState() => _SlidersState();
}

class _SlidersState extends State<_Sliders> {
  double slider1 = 5e0;
  double slider2 = 2e2;
  double slider3 = 1e-5;

  final formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    // double range = context.watch<HomeModel>().range.toDouble();
    return ConstrainedBox(
      constraints: const BoxConstraints(
        maxWidth: 500,
      ),
      child: Column(
        children: <Widget>[
          const Text('Content weight'),
          Slider(
            value: slider1,
            min: 1e-5,
            max: 1e2,
            label: slider1.round().toString(),
            divisions: 1000,
            onChanged: (value) {
              setState(() {
                slider1 = value;
              });
            },
            onChangeEnd: (value) {
              context.read<HomeModel>().contentWeight = value;
            },
          ),
          const SizedBox(height: 10),
          const Text('Style weight'),
          Slider(
            value: slider2,
            min: 1e-5,
            max: 1e4,
            label: slider2.round().toString(),
            divisions: 1000,
            onChanged: (value) {
              setState(() {
                slider2 = value;
              });
            },
            onChangeEnd: (value) {
              context.read<HomeModel>().styleWeight = value;
            },
          ),
          const SizedBox(height: 10),
          const Text('TV weight'),
          Slider(
            value: slider3,
            min: 1e-5,
            max: 1e1,
            label: slider3.toString(),
            divisions: 1000,
            onChanged: (value) {
              setState(() {
                slider3 = value;
              });
            },
            onChangeEnd: (value) {
              context.read<HomeModel>().tvWeight = value;
            },
          ),
        ],
      ),
    );
  }
}
