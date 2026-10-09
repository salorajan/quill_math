# 50 Fundamental Equations of Calculus 1

[← Return to Learn Math Equations Portal](index.html)

Welcome to the Accessible Calculus 1 Reference Guide. This resource provides blind, visually impaired, and sighted learners with 50 foundational equations spanning limits, continuity, single-variable derivatives, optimization, and introductory integration. Every equation includes plain English explanations, clean MathML markup, and in-place hierarchical sub-expression navigation.

---

## 1. Epsilon-Delta Definition of a Limit
$$\forall \varepsilon > 0, \; \exists \delta > 0 : 0 < |x - c| < \delta \implies |f(x) - L| < \varepsilon$$
This is the formal mathematical definition of a limit. It states that as the input $x$ gets arbitrarily close to $c$ (within a small tolerance $\delta$), the output $f(x)$ gets correspondingly close to the target limit $L$ (within tolerance $\varepsilon$). This rigorous definition forms the logical cornerstone of all differential and integral calculus.

---

## 2. Formal Definition of Continuity at a Point
$$\lim_{x \to c} f(x) = f(c)$$
A function is continuous at a point $c$ if three conditions hold: the function is defined at $c$, the two-sided limit as $x$ approaches $c$ exists, and the limit equals the actual function value. Intuitively, this means the graph has no holes, jumps, or vertical asymptotes at that location.

---

## 3. Standard Squeeze Theorem Inequality
$$g(x) \le f(x) \le h(x) \implies \lim_{x \to c} f(x) = L$$
The Squeeze (or Sandwich) Theorem helps find limits of difficult functions by trapping them between two simpler functions $g(x)$ and $h(x)$. If both bounding functions approach the same limit $L$ as $x \to c$, the trapped function $f(x)$ is forced to approach $L$ as well. It is used to prove essential trigonometric limits.

---

## 4. Fundamental Trigonometric Limit
$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$
This fundamental limit shows that for very small angles measured in radians, $\sin x$ is almost equal to $x$ itself. As $x$ approaches zero, the ratio approaches exactly 1, resolving an indeterminate $\frac{0}{0}$ form. This formula is required to prove that the derivative of $\sin x$ is $\cos x$.

---

## 5. Secondary Trigonometric Limit
$$\lim_{x \to 0} \frac{1 - \cos x}{x} = 0$$
This limit evaluates how quickly the cosine curve flattens near $x = 0$. The numerator $(1 - \cos x)$ shrinks much faster than the linear denominator $x$, causing the overall fraction to vanish to zero. It is used alongside the sine limit in the proof of trigonometric derivatives.

---

## 6. Limit Definition of Euler's Number e
$$e = \lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n$$
This equation defines the mathematical constant $e \approx 2.71828$ as the limiting outcome of continuous compounding. As the number of divisions $n$ grows to infinity, the expression converges to the unique base whose exponential function is its own derivative.

---

## 7. Limit Definition of the Derivative
$$f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}$$
This is the foundational definition of the derivative as the limit of the difference quotient. It computes the instantaneous rate of change of a function $f(x)$ at any point $x$ by letting the horizontal gap $h$ between two points shrink to zero. Geometrically, it calculates the exact slope of the tangent line.

---

## 8. Alternative Limit Definition of Derivative at a Point
$$f'(c) = \lim_{x \to c} \frac{f(x) - f(c)}{x - c}$$
This alternative formulation calculates the derivative at a specific fixed point $c$. The denominator $(x - c)$ represents the horizontal run and the numerator represents the vertical rise as the variable point $x$ slides toward the fixed anchor $c$.

---

## 9. Symmetric Difference Quotient
$$f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x - h)}{2h}$$
The symmetric difference quotient averages slopes by stepping equally forward and backward by $h$ around $x$, dividing by the total span $2h$. It converges to the exact derivative with second-order accuracy ($O(h^2)$), making it the standard algorithm for numerical differentiation in computational science.

---

## 10. Power Rule for Differentiation
$$\frac{d}{dx}[x^n] = n x^{n-1}$$
The power rule provides a fast shortcut for taking the derivative of any variable raised to a constant exponent $n$. You bring the exponent $n$ to the front as a multiplying factor and reduce the power by 1. It works for all real powers, including positive integers, negatives, and fractions.

---

## 11. Constant Multiple Rule
$$\frac{d}{dx}[c \cdot f(x)] = c \cdot f'(x)$$
When a function is multiplied by a constant number $c$, you pull the constant outside before differentiating. The rate of change of the scaled function is simply the constant multiplied by the original derivative.

---

## 12. Sum and Difference Rule
$$\frac{d}{dx}[f(x) \pm g(x)] = f'(x) \pm g'(x)$$
The derivative of a sum or difference of two functions is equal to the sum or difference of their individual derivatives. This linearity property allows you to differentiate complex polynomials and multi-term expressions one term at a time.

---

## 13. Product Rule for Derivatives
$$\frac{d}{dx}[f(x) g(x)] = f'(x)g(x) + f(x)g'(x)$$
When differentiating the product of two functions, you cannot simply multiply their derivatives. Instead, take the derivative of the first multiplied by the second, plus the first multiplied by the derivative of the second. This accounts for how changes in both factors simultaneously contribute to the change in area.

---

## 14. Quotient Rule for Derivatives
$$\frac{d}{dx}\left[\frac{f(x)}{g(x)}\right] = \frac{f'(x)g(x) - f(x)g'(x)}{[g(x)]^2}$$
The quotient rule calculates the derivative of a ratio of two functions. In words: "low d-high minus high d-low, all over low squared." The minus sign in the numerator means the order of terms matters, and the denominator function $g(x)$ must not be zero.

---

## 15. The Chain Rule for Composite Functions
$$\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$$
The chain rule differentiates composite (nested) functions where an inner function $g(x)$ is plugged into an outer function $f(u)$. You differentiate the outside function evaluated at the inside, and then multiply by the derivative of the inside function. It is essential for analyzing rates in multi-stage physical systems.

---

## 16. Derivative of the Natural Exponential Function
$$\frac{d}{dx}[e^x] = e^x$$
The natural exponential function $e^x$ is unique because its instantaneous rate of change is equal to its current value. At every single point on its curve, the height of the graph, the slope of the tangent line, and the area under the curve from negative infinity are all identical.

---

## 17. Derivative of General Exponential Functions
$$\frac{d}{dx}[a^x] = a^x \ln(a)$$
When differentiating an exponential function with a base $a > 0$ other than $e$, the result is the original function $a^x$ multiplied by the constant natural logarithm of the base, $\ln(a)$. This extra scaling factor arises directly from the chain rule rewrite $a^x = e^{x \ln a}$.

---

## 18. Derivative of the Natural Logarithm
$$\frac{d}{dx}[\ln x] = \frac{1}{x}$$
The derivative of the natural logarithm $\ln x$ is the reciprocal function $\frac{1}{x}$ for $x > 0$. As $x$ becomes large, the slope approaches zero, explaining why logarithmic growth levels off over time.

---

## 19. Derivative of General Logarithmic Functions
$$\frac{d}{dx}[\log_a x] = \frac{1}{x \ln a}$$
The derivative of a base-$a$ logarithm is $\frac{1}{x}$ divided by the natural logarithm of the base $\ln a$. This formula follows from applying the change of base property $\log_a x = \frac{\ln x}{\ln a}$ before taking the derivative.

---

## 20. Derivative of Sine
$$\frac{d}{dx}[\sin x] = \cos x$$
The rate of change of the sine function at any angle $x$ is given by the cosine function. When sine is at its peak ($x = \pi/2$), cosine is zero, meaning the tangent line is horizontal. When sine crosses zero at $x = 0$, its slope is at a maximum of 1 ($\cos 0 = 1$).

---

## 21. Derivative of Cosine
$$\frac{d}{dx}[\cos x] = -\sin x$$
The derivative of cosine is negative sine. The negative sign reflects that as $x$ increases from $0$ to $\pi$, the cosine curve is sloping downward. Differentiating four times in sequence returns you to the original function.

---

## 22. Derivative of Tangent
$$\frac{d}{dx}[\tan x] = \sec^2 x$$
The derivative of $\tan x$ is $\sec^2 x = \frac{1}{\cos^2 x}$. Because any squared real quantity is non-negative, the slope of the tangent function is always strictly positive wherever the function is defined, meaning $\tan x$ is strictly increasing between its vertical asymptotes.

---

## 23. Derivative of Cotangent
$$\frac{d}{dx}[\cot x] = -\csc^2 x$$
The derivative of the cotangent function is $-\csc^2 x$. The negative sign indicates that the cotangent curve slopes downward everywhere across its continuous domains. This is derived by applying the quotient rule to $\cot x = \frac{\cos x}{\sin x}$.

---

## 24. Derivative of Secant
$$\frac{d}{dx}[\sec x] = \sec x \tan x$$
The derivative of $\sec x = \frac{1}{\cos x}$ is the product of the secant and tangent functions. It is derived using the reciprocal or chain rule on $(\cos x)^{-1}$, producing $\frac{\sin x}{\cos^2 x}$.

---

## 25. Derivative of Cosecant
$$\frac{d}{dx}[\csc x] = -\csc x \cot x$$
The derivative of the cosecant function $\csc x = \frac{1}{\sin x}$ equals $-\csc x \cot x$. Differentiating co-functions (cosine, cotangent, cosecant) always introduces a negative sign in their derivative formulas.

---

## 26. Derivative of Inverse Sine (Arcsine)
$$\frac{d}{dx}[\arcsin x] = \frac{1}{\sqrt{1 - x^2}}$$
The derivative of $\arcsin x$ produces an algebraic expression without any trigonometric functions, valid for $-1 < x < 1$. It is derived via implicit differentiation on $\sin(y) = x$ using the Pythagorean identity $\cos y = \sqrt{1 - \sin^2 y} = \sqrt{1 - x^2}$.

---

## 27. Derivative of Inverse Tangent (Arctangent)
$$\frac{d}{dx}[\arctan x] = \frac{1}{1 + x^2}$$
The derivative of the arctangent function is $\frac{1}{1 + x^2}$, which is defined and smooth for all real numbers $x \in (-\infty, \infty)$. This expression is one of the most widely used antiderivatives in calculus, physics, and electrical engineering.

---

## 28. Derivative of Inverse Secant (Arcsecant)
$$\frac{d}{dx}[\operatorname{arcsec} x] = \frac{1}{|x|\sqrt{x^2 - 1}}$$
The derivative of $\operatorname{arcsec} x$ is defined for $|x| > 1$. The absolute value in the denominator ensures that the derivative remains strictly positive on both disjoint branches of the domain where the function is increasing.

---

## 29. Derivative of an Inverse Function
$$(f^{-1})'(a) = \frac{1}{f'(f^{-1}(a))}$$
This formula calculates the derivative of an inverse function $f^{-1}$ at input $a$ without solving for the inverse explicitly. It equals the reciprocal of the original function's derivative evaluated at the corresponding point $b = f^{-1}(a)$. Geometrically, reflecting a graph over the line $y = x$ inverts its tangent slope.

---

## 30. Equation of the Tangent Line
$$y - f(c) = f'(c)(x - c)$$
This is the point-slope equation of the straight line tangent to the curve $y = f(x)$ at the point $(c, f(c))$. The derivative $f'(c)$ provides the exact slope of the line. The tangent line is the best local linear approximation to the curve near $x = c$.

---

## 31. Linear Approximation / Tangent Line Approximation
$$L(x) = f(a) + f'(a)(x - a)$$
The linear approximation $L(x)$ replaces a complicated non-linear curve with its tangent line near an anchor point $a$. It allows quick estimation of function values for inputs $x$ close to $a$ without expensive computation.

---

## 32. Differential Relationship
$$dy = f'(x) dx$$
In Leibniz notation, differentials represent tiny changes: $dx$ is an independent change in the input, and $dy$ is the corresponding linear change in the output along the tangent line. Differentials provide an intuitive basis for error propagation analysis and substitution in integration.

---

## 33. Intermediate Value Theorem Condition
$$f(a) < k < f(b) \implies \exists c \in (a, b) : f(c) = k$$
The Intermediate Value Theorem (IVT) states that a continuous function on a closed interval $[a, b]$ takes on every single value $k$ between $f(a)$ and $f(b)$. Geometrically, a continuous path cannot cross from one elevation to another without crossing every intermediate height. It guarantees the existence of solutions to non-linear equations.

---

## 34. Rolle's Theorem Condition
$$f(a) = f(b) \implies \exists c \in (a, b) : f'(c) = 0$$
Rolle's Theorem states that if a differentiable function has equal values at both endpoints of an interval ($f(a) = f(b)$), there must be at least one point $c$ in between where the tangent line is completely flat ($f'(c) = 0$). It is a special case of the Mean Value Theorem.

---

## 35. Mean Value Theorem for Derivatives
$$f'(c) = \frac{f(b) - f(a)}{b - a}$$
The Mean Value Theorem (MVT) bridges average change and instantaneous change. It guarantees that for a smooth continuous curve on $[a, b]$, there is at least one interior point $c$ where the instantaneous slope $f'(c)$ equals the average secant slope over the entire interval.

---

## 36. Cauchy's Extended Mean Value Theorem
$$\frac{f'(c)}{g'(c)} = \frac{f(b) - f(a)}{g(b) - g(a)}$$
Cauchy's Extended Mean Value Theorem generalizes the MVT to two parametric functions $f(x)$ and $g(x)$. It shows that the ratio of instantaneous rates at some point $c$ equals the ratio of their total changes over the interval. It serves as the formal foundation for proving L'Hopital's Rule.

---

## 37. L'Hopital's Rule for Indeterminate Limits
$$\lim_{x \to c} \frac{f(x)}{g(x)} = \lim_{x \to c} \frac{f'(x)}{g'(x)}$$
When a limit produces an indeterminate fraction of the form $\frac{0}{0}$ or $\frac{\pm\infty}{\pm\infty}$, L'Hopital's Rule allows you to differentiate the numerator and denominator separately. You then re-evaluate the limit of the new fraction.

---

## 38. Second Derivative Test for Local Extrema
$$f'(c) = 0 \land f''(c) > 0 \implies \text{Local Minimum at } x = c$$
When the first derivative is zero (a critical point), the second derivative measures the curve's concavity. If $f''(c) > 0$, the curve is concave up (bending upward like a cup), confirming that $(c, f(c))$ is a local minimum. If $f''(c) < 0$, it is concave down and represents a local maximum.

---

## 39. Point of Inflection Condition
$$f''(c) = 0 \text{ with concavity change across } x = c$$
An inflection point occurs where a graph transitions between being concave upward and concave downward. While $f''(c) = 0$ or is undefined at candidate locations, an inflection point is confirmed only if the sign of $f''(x)$ actually flips across $x = c$.

---

## 40. Newton-Raphson Root-Finding Iteration Formula
$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$
The Newton-Raphson method is an efficient algorithm to approximate numerical roots of $f(x) = 0$. Starting from an initial guess $x_0$, each iteration follows the tangent line down to the x-axis to produce a dramatically improved estimate $x_{n+1}$, doubling accuracy digits with each step.

---

## 41. Definition of the Definite Integral as a Riemann Sum
$$\int_{a}^{b} f(x) dx = \lim_{n \to \infty} \sum_{i=1}^{n} f(x_i^*) \Delta x$$
The definite integral computes the exact net signed area under a curve by slicing the region into $n$ thin vertical rectangular strips of width $\Delta x = \frac{b - a}{n}$. As the number of strips $n$ approaches infinity, the sum of rectangle areas converges to the continuous integral.

---

## 42. Fundamental Theorem of Calculus Part 1 (Differentiation of Integrals)
$$\frac{d}{dx} \int_{a}^{x} f(t) dt = f(x)$$
This theorem establishes that integration and differentiation are inverse mathematical operations. Taking the derivative of an accumulation area function with respect to its upper limit $x$ simply returns the original integrand function $f(x)$.

---

## 43. Fundamental Theorem of Calculus Part 2 (Evaluation Theorem)
$$\int_{a}^{b} f(x) dx = F(b) - F(a)$$
The evaluation theorem allows you to compute definite integrals easily without taking limits of Riemann sums. You find any antiderivative $F(x)$ such that $F'(x) = f(x)$, and subtract the value at the lower limit from the value at the upper limit.

---

## 44. Mean Value Theorem for Definite Integrals
$$f(c) = \frac{1}{b - a} \int_{a}^{b} f(x) dx$$
This theorem states that a continuous function on $[a, b]$ always achieves its exact average (mean) value at some point $c$ inside the interval. Geometrically, the area under the curve equals the area of a single rectangle with width $(b - a)$ and height $f(c)$.

---

## 45. Power Rule for Indefinite Integration
$$\int x^n dx = \frac{x^{n+1}}{n+1} + C \quad (n \ne -1)$$
To integrate a power $x^n$, you add 1 to the exponent and divide by the new exponent, adding an arbitrary constant of integration $C$. This rule works for all powers except $n = -1$, which would cause division by zero.

---

## 46. Logarithmic Integration Rule
$$\int \frac{1}{x} dx = \ln|x| + C$$
The antiderivative of the reciprocal function $\frac{1}{x}$ is the natural logarithm of the absolute value of $x$, plus constant $C$. The absolute value bars ensure the domain includes both positive and negative real numbers.

---

## 47. Exponential Integration Rule
$$\int e^{k x} dx = \frac{1}{k} e^{k x} + C$$
Integrating an exponential function with linear scaling $kx$ reproduces the original exponential divided by the constant rate factor $k$, plus constant $C$. It is the direct inverse of the exponential chain rule.

---

## 48. Integration by u-Substitution (Indefinite Form)
$$\int f(g(x)) g'(x) dx = \int f(u) du$$
Integration by substitution is the chain rule in reverse. By setting a new variable $u = g(x)$ and differential $du = g'(x)dx$, a complicated integral transforms into a much simpler antiderivative problem in terms of $u$.

---

## 49. Definite Integral Substitution Rule
$$\int_{a}^{b} f(g(x)) g'(x) dx = \int_{g(a)}^{g(b)} f(u) du$$
When performing u-substitution on a definite integral, you change the integration limits from $x$-values ($a, b$) to their corresponding $u$-values ($g(a), g(b)$). This eliminates the need to back-substitute into $x$ after finding the antiderivative.

---

## 50. Total Net Change Theorem
$$\int_{t_1}^{t_2} f'(t) dt = f(t_2) - f(t_1)$$
The net change theorem states that the integral of a rate of change gives the total accumulated change in the quantity over time. For example, integrating velocity yields total displacement, and integrating power over time gives total energy consumed.
