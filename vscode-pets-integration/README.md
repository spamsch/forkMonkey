# VS Code Pets Integration - Fork Monkey

This directory contains all files and documentation needed to integrate the Fork Monkey pet into the [VS Code Pets extension](https://github.com/tonybaloney/vscode-pets).

## 📁 Directory Structure

```
vscode-pets-integration/
├── assets/
│   └── fork-monkey/
│       ├── brown_idle_8fps.gif      # Idle animation (4 frames)
│       ├── brown_walk_8fps.gif      # Walk animation (6 frames)
│       ├── brown_run_8fps.gif       # Run animation (8 frames)
│       ├── brown_swipe_8fps.gif     # Swipe/eat animation (5 frames)
│       ├── brown_with_ball_8fps.gif # With ball animation (4 frames)
│       └── README.md                # Asset documentation
├── scripts/
│   └── sprite-generation/
│       ├── generate_forkmonkey.py   # AI frame generation using Gemini
│       ├── assemble_gifs.py         # GIF assembly from PNG frames
│       ├── test_gemini.py           # API connection test
│       └── README.md                # Script documentation
├── docs/
│   └── (integration guides will go here)
└── README.md                        # This file
```

## 🎨 Assets

All Fork Monkey animations are located in `assets/fork-monkey/`:

| Animation | Frames | Size | FPS | Dimensions | Description |
|-----------|--------|------|-----|------------|-------------|
| idle | 4 | 13.8 KB | 4 | 111×101 | Standing with breathing |
| walk | 6 | 20.8 KB | 4 | 111×101 | Walking animation |
| run | 8 | 28.0 KB | 4 | 111×101 | Running fast |
| swipe | 5 | 17.1 KB | 4 | 111×101 | Using fork to eat |
| with_ball | 4 | 13.6 KB | 4 | 111×101 | Holding a ball |

**Total Size:** 93.2 KB

### Technical Specifications

- **Format:** Animated GIF
- **Dimensions:** 111×101 pixels (matches VS Code Pets standard)
- **Frame Rate:** 4 FPS (250ms per frame)
- **Color Mode:** Indexed color with transparency
- **Disposal Method:** Background (2)
- **Optimization:** Enabled
- **Transparency:** Binary (no semi-transparent pixels)

## 🤖 Generation Scripts

### Prerequisites

```bash
# Install required packages
sudo pip3 install google-genai pillow

# Set API key
export GEMINI_API_KEY="your-api-key-here"
```

### Frame Generation

Generate individual animation frames using Gemini AI:

```bash
cd scripts/sprite-generation
python3 generate_forkmonkey.py
```

This will create 28 PNG frames (1024×1024) in the `frames/` directory.

### GIF Assembly

Convert PNG frames to optimized animated GIFs:

```bash
cd scripts/sprite-generation
python3 assemble_gifs.py
```

This will create 5 GIF files in the `gifs/` directory.

## 🔧 Integration Steps

### Step 1: Copy Assets

Copy the GIF files to the VS Code Pets media directory:

```bash
cp assets/fork-monkey/*.gif /path/to/vscode-pets/media/fork-monkey/
```

### Step 2: Create Pet Class

Create `src/panel/pets/fork-monkey.ts`:

```typescript
import { PetColor, PetSpeed, PetSize } from '../pets';
import { BasePetType } from '../basepettype';

export class ForkMonkey extends BasePetType {
    label = 'fork-monkey';
    static possibleColors = [PetColor.brown];
    static count: number = 0;

    constructor(
        spriteElement: HTMLImageElement,
        collisionElement: HTMLDivElement,
        speechElement: HTMLDivElement,
        size: PetSize,
        left: number,
        bottom: number,
        petRoot: string,
        floor: number,
        name: string,
        speed: PetSpeed,
        generation: number,
    ) {
        super(
            spriteElement,
            collisionElement,
            speechElement,
            size,
            left,
            bottom,
            petRoot,
            floor,
            name,
            speed,
            generation,
        );
        ForkMonkey.count++;
    }

    remove() {
        ForkMonkey.count--;
        super.remove();
    }
}
```

### Step 3: Update Type Definitions

Add to `src/panel/pets.ts`:

```typescript
export const FORK_MONKEY_NAMES: ReadonlyArray<string> = [
    'Forky',
    'Monty',
    'Banana',
    'Chip',
    'Nibbles',
    // Add more names...
];
```

### Step 4: Register in Pet Factory

Update `src/panel/pets.ts` to include Fork Monkey in the pet factory.

### Step 5: Test Locally

```bash
cd /path/to/vscode-pets
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

## 📊 Quality Comparison

| Metric | VS Code Pets Standard | Fork Monkey | Status |
|--------|----------------------|-------------|---------|
| Dimensions | 111×101 | 111×101 | ✅ Match |
| Frame Rate | 4 FPS | 4 FPS | ✅ Match |
| File Size | ~8-30 KB | 13-28 KB | ✅ Similar |
| Transparency | Clean | Clean | ✅ Match |
| Animation Count | 5 | 5 | ✅ Match |
| Pixel Art Style | Yes | Yes | ✅ Match |

## 🎯 Next Steps

1. ✅ Generate Fork Monkey sprites with AI
2. ✅ Create animated GIFs with proper transparency
3. ✅ Optimize file sizes
4. ⏳ Create TypeScript integration code
5. ⏳ Test locally in VS Code Pets
6. ⏳ Submit pull request to vscode-pets repository

## 📝 Notes

- All animations use **binary transparency** (no semi-transparent pixels) to ensure clean rendering
- The Fork Monkey character design features a brown monkey holding a golden fork
- Generated using **Gemini 2.5 Flash Image (Nano Banana)** AI model
- Frame assembly uses **Pillow** with custom transparency handling

## 🔗 References

- [VS Code Pets Repository](https://github.com/tonybaloney/vscode-pets)
- [Fork Monkey Issue #850](https://github.com/tonybaloney/vscode-pets/issues/850)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

## 📜 License

The Fork Monkey assets and code are intended for integration into VS Code Pets and follow the same license as the main project.

---

**Created:** December 24, 2025  
**Author:** Levi Law (with Manus AI assistance)  
**Status:** Ready for integration testing
