import 'dart:typed_data';

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

  @override
  Widget build(BuildContext context) {
    var model = context.read<HomeModel>();
    var submit = context.watch<HomeModel>().content != null &&
        context.watch<HomeModel>().style != null;
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
            model.content = res;
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
            width: 500,
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
          FilledButton(
            onPressed: () {
              if (formKey.currentState != null &&
                  formKey.currentState!.validate()) {
                context.read<HomeModel>().save();
              }
            },
            child: const Text('Save options'),
          ),
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
    return Form(
      key: formKey,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: <Widget>[
          _SizeSelectors(),
          ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: 150,
            ),
            child: Form(
              child: TextFormField(
                controller: context.read<HomeModel>().rangeController,
                decoration: const InputDecoration(
                  labelText: 'Range',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null) return null;
                  try {
                    int res = int.parse(value);
                    if (res < 10 || res > 10000) {
                      return 'from 10 to 10000';
                    }
                    return null;
                  } catch (_) {
                    return 'Invalid range number';
                  }
                },
                onChanged: (value) {
                  try {
                    var res = int.parse(value);
                    if (res >= 10 && res <= 10000) {
                      context.read<HomeModel>().setRange(res);
                    }
                  } catch (_) {}
                },
              ),
            ),
          ),
          _Sliders(),
        ],
      ),
    );
  }
}

class _SizeSelectors extends StatelessWidget {
  // final formKey = GlobalKey<FormState>();
  @override
  Widget build(BuildContext context) {
    var model = context.read<HomeModel>();
    return ConstrainedBox(
      constraints: const BoxConstraints(
        maxWidth: 150,
      ),
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
                if (res < 256 || res > 1024) {
                  return 'from 256 to 1024';
                }
                return null;
              } catch (_) {
                return 'Invalid number';
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
                if (res < 256 || res > 1024) {
                  return 'from 256 to 1024';
                }
                return null;
              } catch (_) {
                return 'Invalid number';
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
          ),
        ],
      ),
    );
  }
}

class _Sliders extends StatefulWidget {
  @override
  State<_Sliders> createState() => _SlidersState();
}

class _SlidersState extends State<_Sliders> {
  double slider1 = 0;
  double slider2 = 0;
  double slider3 = 0;

  final formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    double range = context.watch<HomeModel>().range.toDouble();
    return ConstrainedBox(
      constraints: const BoxConstraints(
        maxWidth: 400,
      ),
      child: Column(
        children: <Widget>[
          const Text('Content weight'),
          Slider(
            value: slider1,
            min: -range,
            max: range,
            label: slider1.round().toString(),
            divisions: range ~/ 10,
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
          const Text('TV weight'),
          Slider(
            value: slider2,
            min: -range,
            max: range,
            label: slider2.round().toString(),
            divisions: range ~/ 10,
            onChanged: (value) {
              setState(() {
                slider2 = value;
              });
            },
            onChangeEnd: (value) {
              context.read<HomeModel>().tvWeight = value;
            },
          ),
          const SizedBox(height: 10),
          const Text('Style weight'),
          Slider(
            value: slider3,
            min: -range,
            max: range,
            label: slider3.round().toString(),
            divisions: range ~/ 10,
            onChanged: (value) {
              setState(() {
                slider3 = value;
              });
            },
            onChangeEnd: (value) {
              context.read<HomeModel>().styleWeight = value;
            },
          ),
        ],
      ),
    );
  }
}
