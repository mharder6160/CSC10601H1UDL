# Sample Module: Java Foundations (Program Structure, Variables, Data Types, Input/Output)

**Suggested placement:** Early term (after course orientation; aligns with introductory Java sequence)  
**Estimated Time:** 6-8 hours

## 1) Overview

This module introduces the structure of a Java program and core building blocks: variables, data types, and console input/output. You will write and test simple programs that read user input, perform calculations, and print formatted results.

## 2) Learning Outcomes

By the end of this module, students will be able to:

1. Identify the required structure of a basic Java class with a `main` method.
2. Declare and initialize variables using appropriate primitive data types.
3. Accept keyboard input and produce clear output.
4. Trace simple expressions and explain resulting values.

## 3) Materials

- Assigned reading: Intro Java chapter sections on basic syntax, variables, and input/output [INSTRUCTOR CONFIRM chapter/sections]
- Existing course slide deck for introductory programming [INSTRUCTOR CONFIRM exact file]
- IDE/JDK setup from Start Here module

## 4) Vocabulary

- **Class**: A blueprint for creating objects; also a container for methods in introductory programs.
- **Method**: A block of code that performs a task.
- **`main` method**: The entry point where Java starts program execution.
- **Variable**: A named storage location for a value.
- **Data type**: Defines what kind of data a variable stores (e.g., `int`, `double`, `String`).
- **Input**: Data read into a program.
- **Output**: Information printed or displayed by a program.

## 5) Mini-lesson

### A. Basic Java program structure

```java
public class HelloUser {
    public static void main(String[] args) {
        System.out.println("Hello, Java student!");
    }
}
```

Key parts:

- `public class HelloUser` -> class name should match filename `HelloUser.java`
- `main` method -> program starts here
- `System.out.println(...)` -> prints text and moves to a new line

### B. Variables and data types

```java
int age = 18;
double gpa = 3.25;
char gradeLetter = 'A';
boolean enrolled = true;
String name = "Alex";
```

Choose data types based on what values you need to store.

### C. Input and output with `Scanner`

```java
import java.util.Scanner;

public class IntroIO {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter your name: ");
        String name = input.nextLine();

        System.out.print("Enter your age: ");
        int age = input.nextInt();

        System.out.println("Welcome, " + name + ". Next year you will be " + (age + 1) + ".");

        input.close();
    }
}
```

## 6) Worked example

### Problem

Write a program that reads a student's first name and two quiz scores, then prints the average score.

### Pseudocode

1. Start program
2. Ask for first name
3. Ask for quiz1 and quiz2
4. Compute average `(quiz1 + quiz2) / 2.0`
5. Print name and average
6. End program

### Java solution

```java
import java.util.Scanner;

public class QuizAverage {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);

        System.out.print("First name: ");
        String firstName = in.nextLine();

        System.out.print("Quiz 1 score: ");
        double quiz1 = in.nextDouble();

        System.out.print("Quiz 2 score: ");
        double quiz2 = in.nextDouble();

        double average = (quiz1 + quiz2) / 2.0;

        System.out.printf("%s, your average is %.2f%n", firstName, average);

        in.close();
    }
}
```

### Text trace table

Given input: `Mia`, `84`, `92`

| Step | quiz1 | quiz2 | average | Output note |
|---|---:|---:|---:|---|
| After reading quiz1 | 84.0 | not yet set | not yet set | no final output yet |
| After reading quiz2 | 84.0 | 92.0 | not yet set | no final output yet |
| After compute | 84.0 | 92.0 | 88.0 | prints: `Mia, your average is 88.00` |

## 7) Guided practice

### Practice A (with hints)

Create `RectangleArea.java`:

- Input width and height as `double`
- Compute `area = width * height`
- Print area to two decimal places

Hint: use `System.out.printf("Area: %.2f%n", area);`

### Practice B (with partial starter)

```java
// Complete missing lines marked TODO
import java.util.Scanner;

public class TemperatureCheck {
    public static void main(String[] args) {
        Scanner kb = new Scanner(System.in);

        // TODO: read a temperature in Celsius
        // TODO: convert to Fahrenheit using F = C * 9 / 5 + 32
        // TODO: print both values

        kb.close();
    }
}
```

## 8) Independent practice

1. Write `CircleMetrics.java` that reads a radius and outputs diameter, circumference, and area.
2. Write `PayEstimate.java` that reads hourly rate and hours worked and prints estimated pay.

For each program:

- Include clear prompts
- Use meaningful variable names
- Use formatted output where appropriate

## 9) Troubleshooting / common errors

- **`class X is public, should be declared in a file named X.java`**
  - Fix: filename and public class name must match exactly.
- **`cannot find symbol`**
  - Fix: check spelling/case of variable or method names.
- **`InputMismatchException`**
  - Fix: entered text when numeric input was expected; retry with numeric value.
- **No output appears**
  - Fix: verify code is running the latest saved file and the expected class.

## 10) Knowledge check (low stakes)

1. Which method starts a Java application?
2. Which data type would you use for a decimal value like GPA?
3. What does `System.out.print` do compared with `System.out.println`?
4. Given `int x = 7; int y = 2;`, what is `x / y`?
5. Why is `(x + y) / 2.0` often used instead of `(x + y) / 2` for averages?

Instructor note: configure immediate feedback in D2L quiz settings.

## 11) Programming assignment (graded)

### Assignment title

**Student Info Summary Program**

### Prompt

Write a Java program named `StudentSummary.java` that:

1. Prompts for student name (`String`)
2. Prompts for number of completed credits (`int`)
3. Prompts for current GPA (`double`)
4. Computes estimated remaining credits to `60` total using `remaining = Math.max(0, 60 - completed)` so remaining credits never display as negative
5. Prints a clear summary with labels and formatted GPA (2 decimals)

For this assignment, use `Math.max(0, 60 - completed)` so remaining credits never display as a negative value.

### Starter-code expectations

Students may start from a provided skeleton file that includes:

- class declaration
- `main` method
- `Scanner` setup/close
- TODO markers for prompts, variables, calculation, and output

### Required submission

- `StudentSummary.java`
- short test log (plain text or doc) with **at least 3 test cases**, including one edge case

### Testing guidance

Use test inputs covering:

- normal case (e.g., completed `24`, GPA `3.10`)
- near-completion case (e.g., completed `59`)
- boundary/edge consideration (e.g., completed `60`)
- over-completion case (e.g., completed `72`) and confirm remaining credits prints as `0`

Expected checks:

- Program compiles with no errors
- Prompts are understandable
- Math is correct
- Output formatting is readable

### Rubric (20 points)

| Criteria | Exceeds | Meets | Developing | Points |
|---|---|---|---|---:|
| Program correctness | All required behaviors + accurate calculations | Required behaviors mostly correct | Missing major requirement(s) | 8 |
| Java syntax & data type use | Correct and consistent | Minor syntax/type issues | Repeated syntax/type errors | 4 |
| Input/output clarity | Clear prompts + well-formatted output | Understandable prompts/output | Confusing or incomplete I/O | 4 |
| Testing evidence | 3+ meaningful tests incl. edge case with results | 3 tests with partial detail | Fewer than 3 or unclear test evidence | 4 |

## 12) Reflection

- What bug or confusion took the most time this week?
- What debugging action was most helpful?
- What is one question you want to ask before the next module?

## 13) Accessibility and alternative format notes

- Provide this module in D2L HTML and downloadable text format.
- If a video walkthrough is added, include captions and transcript.
- Keep code examples in copyable text (not image-only).
- For tables, retain header row structure for screen readers.
