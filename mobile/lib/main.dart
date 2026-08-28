import 'package:flutter/material.dart';

import 'theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ArkApp());
}

const String limitation =
    'Not a kernel, not a bootable OS, not a worm, not kernel isolation. '
    '"Rotating Kernel" means the rotating crypto/engine. This app is the '
    'dome UI. The crypto engine is the desktop ark package. Offline. '
    'Forgotten phrase = permanent loss. Civilian software.';

class ArkApp extends StatelessWidget {
  const ArkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'The ARK',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const ArkHome(),
    );
  }
}

class ArkHome extends StatefulWidget {
  const ArkHome({super.key});

  @override
  State<ArkHome> createState() => _ArkHomeState();
}

class _ArkHomeState extends State<ArkHome> {
  final _phrase = TextEditingController();
  String _level = 'normal';
  bool _unlocked = false;
  final List<String> _placeholder = const [
    '(empty vault — wrong phrase also looks like this)',
  ];

  @override
  void dispose() {
    _phrase.dispose();
    super.dispose();
  }

  void _unlock() {
    _phrase.clear();
    setState(() => _unlocked = true);
  }

  void _lock() {
    _phrase.clear();
    setState(() => _unlocked = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('The ARK')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Aziel Rotating Kernel. Local deniable vault. Not a kernel.',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(color: kGold),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Text(limitation, style: Theme.of(context).textTheme.bodyMedium),
            ),
          ),
          const SizedBox(height: 18),
          TextField(
            controller: _phrase,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Phrase (this IS the login)',
              helperText: 'Never stored in the cloud. Dome UI only.',
            ),
          ),
          const SizedBox(height: 12),
          Text('Security level (behavior, not crypto)', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'normal', label: Text('normal')),
              ButtonSegment(value: 'strong', label: Text('strong')),
              ButtonSegment(value: 'paranoid', label: Text('paranoid')),
            ],
            selected: {_level},
            onSelectionChanged: (s) => setState(() => _level = s.first),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              FilledButton(onPressed: _unlock, child: const Text('Unlock')),
              const SizedBox(width: 12),
              OutlinedButton(onPressed: _lock, child: const Text('Lock')),
            ],
          ),
          const SizedBox(height: 24),
          Text(_unlocked ? 'Vault list (placeholder — engine is desktop)' : 'Locked',
              style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 8),
          if (_unlocked)
            ..._placeholder.map(
              (row) => Card(
                child: ListTile(
                  title: Text(row),
                  subtitle: Text('level $_level'),
                ),
              ),
            ),
          const SizedBox(height: 24),
          Text(
            'Counted desktop download: https://ark-download-tracker.vibelock.workers.dev/',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(color: kGoldDim),
          ),
        ],
      ),
    );
  }
}
