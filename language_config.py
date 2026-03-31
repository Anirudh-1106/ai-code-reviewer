LANGUAGE_ALIASES = {
    "python": "Python",
    "py": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c": "C",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "rs": "Rust",
}

LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "JavaScript": ".js",
    "TypeScript": ".ts",
    "Java": ".java",
    "C++": ".cpp",
    "C": ".c",
    "Go": ".go",
    "Rust": ".rs",
}

TREE_SITTER_LANGUAGE_NAMES = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "java",
    "C++": "cpp",
    "C": "c",
    "Go": "go",
    "Rust": "rust",
}

LANGUAGE_DEMOS = {
    "Python": (
        "import os\n"
        "\n"
        "def add_numbers(nums):\n"
        "    total = 0\n"
        "    for i in range(len(nums)):\n"
        "        total += nums[i]\n"
        "    return total\n"
        "\n"
        "unused_var = 42\n"
        "print(add_numbers([1,2,3]))\n"
    ),
    "JavaScript": (
        "import fs from 'fs';\n"
        "\n"
        "function sum(nums) {\n"
        "  let total = 0;\n"
        "  for (let i = 0; i < nums.length; i++) {\n"
        "    total += nums[i];\n"
        "  }\n"
        "  return total;\n"
        "}\n"
        "\n"
        "const unusedVar = 42;\n"
        "console.log(sum([1, 2, 3]));\n"
    ),
    "TypeScript": (
        "function sum(nums: number[]): number {\n"
        "  let total = 0;\n"
        "  for (let i = 0; i < nums.length; i++) {\n"
        "    total += nums[i];\n"
        "  }\n"
        "  return total;\n"
        "}\n"
        "\n"
        "const unusedValue: number = 42;\n"
        "console.log(sum([1, 2, 3]));\n"
    ),
    "Java": (
        "import java.util.*;\n"
        "\n"
        "class Main {\n"
        "  static int sum(int[] nums) {\n"
        "    int total = 0;\n"
        "    for (int i = 0; i < nums.length; i++) total += nums[i];\n"
        "    return total;\n"
        "  }\n"
        "}\n"
    ),
    "C++": (
        "#include <iostream>\n"
        "using namespace std;\n"
        "\n"
        "int sum(int nums[], int n) {\n"
        "  int total = 0;\n"
        "  for (int i = 0; i < n; i++) total += nums[i];\n"
        "  return total;\n"
        "}\n"
    ),
    "C": (
        "#include <stdio.h>\n"
        "\n"
        "int sum(int nums[], int n) {\n"
        "  int total = 0;\n"
        "  for (int i = 0; i < n; i++) total += nums[i];\n"
        "  return total;\n"
        "}\n"
    ),
    "Go": (
        "package main\n"
        "\n"
        "import \"fmt\"\n"
        "\n"
        "func sum(nums []int) int {\n"
        "  total := 0\n"
        "  for i := 0; i < len(nums); i++ {\n"
        "    total += nums[i]\n"
        "  }\n"
        "  return total\n"
        "}\n"
    ),
    "Rust": (
        "fn sum(nums: &[i32]) -> i32 {\n"
        "    let mut total = 0;\n"
        "    for i in 0..nums.len() {\n"
        "        total += nums[i];\n"
        "    }\n"
        "    total\n"
        "}\n"
    ),
}


def normalize_language(language: str) -> str:
    if not language:
        return "Python"
    key = language.strip().lower()
    return LANGUAGE_ALIASES.get(key, "Python")


def supported_languages() -> list[str]:
    return list(LANGUAGE_EXTENSIONS.keys())
