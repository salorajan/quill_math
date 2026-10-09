# 50 Fundamental Equations of Calculus 2

[← Return to Learn Math Equations Portal](index.html)

Welcome to the Accessible Calculus 2 Reference Guide. This resource provides blind, visually impaired, and sighted students with an intuitive reference of 50 advanced single-variable equations spanning integration techniques, geometrical applications, differential equations, polar/parametric coordinates, and infinite series. Every equation features plain English explanations, clean MathML markup, and in-place hierarchical sub-expression navigation.

---

## 1. Integration by Parts Formula
$$\int u \, dv = u v - \int v \, du$$
Integration by parts is the product rule of differentiation in reverse. It allows you to transform an intractable integral into a simpler one by strategically assigning one part of the integrand to $u$ (which gets differentiated to $du$) and the remaining part to $dv$ (which gets integrated to $v$).

---

## 2. Definite Integration by Parts
$$\int_{a}^{b} u \, dv = [u(x) v(x)]_{a}^{b} - \int_{a}^{b} v \, du$$
This is the definite integral version of integration by parts. The boundary evaluation bracket $[u(x) v(x)]_a^b = u(b)v(b) - u(a)v(a)$ evaluates the boundary term immediately before computing the remaining definite integral.

---

## 3. Trigonometric Substitution for a Squared Minus x Squared
$$x = a \sin \theta \implies \sqrt{a^2 - x^2} = a \cos \theta$$
When an integrand contains the radical term $\sqrt{a^2 - x^2}$, substituting $x = a \sin \theta$ eliminates the square root using the trigonometric identity $1 - \sin^2 \theta = \cos^2 \theta$. This converts algebraic root expressions into clean trigonometric powers.

---

## 4. Trigonometric Substitution for a Squared Plus x Squared
$$x = a \tan \theta \implies \sqrt{a^2 + x^2} = a \sec \theta$$
When dealing with expressions containing $\sqrt{a^2 + x^2}$ or $(a^2 + x^2)$, substituting $x = a \tan \theta$ simplifies the expression using the identity $1 + \tan^2 \theta = \sec^2 \theta$, replacing the addition under the radical with a single squared term.

---

## 5. Trigonometric Substitution for x Squared Minus a Squared
$$x = a \sec \theta \implies \sqrt{x^2 - a^2} = a \tan \theta$$
For expressions involving $\sqrt{x^2 - a^2}$, substituting $x = a \sec \theta$ simplifies the square root via the identity $\sec^2 \theta - 1 = \tan^2 \theta$. This is standard for integrating rational functions with negative constant terms under square roots.

---

## 6. Partial Fraction Decomposition for Distinct Linear Factors
$$\frac{P(x)}{(x - r_1)(x - r_2)} = \frac{A}{x - r_1} + \frac{B}{x - r_2}$$
Partial fraction decomposition breaks down a complicated rational function into a sum of simpler fractions with linear denominators. Each simple fraction can then be integrated directly to produce natural logarithm terms $\ln|x - r|$.

---

## 7. Partial Fraction Decomposition for Irreducible Quadratic Factors
$$\frac{P(x)}{(x - r)(x^2 + bx + c)} = \frac{A}{x - r} + \frac{Bx + C}{x^2 + bx + c}$$
When a denominator contains an irreducible quadratic factor $(x^2 + bx + c)$ that cannot be factored into real linear terms, its partial fraction numerator must be a linear polynomial $(Bx + C)$. Integrating this term typically yields a combination of natural logarithms and arctangent functions.

---

## 8. Reduction Formula for Sine Powers
$$\int \sin^n x \, dx = -\frac{\sin^{n-1} x \cos x}{n} + \frac{n-1}{n} \int \sin^{n-2} x \, dx$$
This recursive formula reduces the power of an integrated sine function by 2 at each step using integration by parts. Repeating this reduction brings any high integer power down to either $\int 1 \, dx = x$ (for even powers) or $\int \sin x \, dx = -\cos x$ (for odd powers).

---

## 9. Reduction Formula for Cosine Powers
$$\int \cos^n x \, dx = \frac{\cos^{n-1} x \sin x}{n} + \frac{n-1}{n} \int \cos^{n-2} x \, dx$$
Similar to the sine reduction formula, this equation reduces the exponent of $\cos^n x$ by two steps per iteration. It is widely used in physics and Fourier analysis to integrate higher-harmonic waveforms over full periods.

---

## 10. Integral of Secant Function
$$\int \sec x \, dx = \ln|\sec x + \tan x| + C$$
The integral of $\sec x$ is derived by multiplying numerator and denominator by $(\sec x + \tan x)$ to set up a natural logarithmic u-substitution. This formula is essential when completing trigonometric substitutions and calculating arc lengths of parabolas.

---

## 11. Area Between Two Curves
$$A = \int_{a}^{b} [f(x) - g(x)] \, dx$$
This formula computes the two-dimensional area enclosed between an upper curve $f(x)$ and a lower curve $g(x)$ from $x = a$ to $x = b$. By subtracting the lower height from the upper height at each point, it sums the infinitesimal vertical strips $[f(x) - g(x)]dx$.

---

## 12. Volume by the Disk Method (Revolution About x-Axis)
$$V = \pi \int_{a}^{b} [f(x)]^2 \, dx$$
The disk method calculates the volume of a solid of revolution created by rotating a continuous curve $y = f(x)$ around the horizontal x-axis. Each infinitesimal cross-section is a circular disk with radius $r = f(x)$ and area $\pi r^2 = \pi [f(x)]^2$.

---

## 13. Volume by the Washer Method (Revolution About x-Axis)
$$V = \pi \int_{a}^{b} \left([R(x)]^2 - [r(x)]^2\right) \, dx$$
When a region between two curves is rotated around an axis, the cross-sections are flat washers with a hole in the center. The volume integrates the difference between the outer circular area $\pi [R(x)]^2$ and the inner circular hole area $\pi [r(x)]^2$.

---

## 14. Volume by Cylindrical Shells (Revolution About y-Axis)
$$V = 2\pi \int_{a}^{b} x f(x) \, dx$$
The shell method calculates the volume of a solid rotated around the y-axis by integrating nested thin cylindrical shells. The formula multiplies the circumference of the shell ($2\pi x$) by its height ($f(x)$) and thickness ($dx$).

---

## 15. Arc Length of a Cartesian Curve
$$L = \int_{a}^{b} \sqrt{1 + [f'(x)]^2} \, dx$$
This formula calculates the physical length of a smooth curve $y = f(x)$ between $x = a$ and $x = b$. Derived from the Pythagorean theorem on infinitesimal differentials $dL = \sqrt{dx^2 + dy^2}$, it factors out $dx$ to integrate the root of one plus the squared derivative.

---

## 16. Surface Area of Revolution (About x-Axis)
$$S = 2\pi \int_{a}^{b} f(x) \sqrt{1 + [f'(x)]^2} \, dx$$
Rotating a curve $y = f(x)$ around the x-axis sweeps out a three-dimensional surface. This formula computes the total surface area by multiplying each slice's circular perimeter ($2\pi f(x)$) by its slant arc length element ($dL = \sqrt{1 + (f')^2}dx$).

---

## 17. Work Done by a Variable Force
$$W = \int_{a}^{b} F(x) \, dx$$
In physics, mechanical work equals force multiplied by distance. When the applied force $F(x)$ varies as an object moves along a path from $x = a$ to $x = b$ (such as stretching a non-linear spring or pumping liquid out of a tank), total work is computed by integrating the force function.

---

## 18. Center of Mass (Centroid) Coordinates
$$\bar{x} = \frac{1}{A} \int_{a}^{b} x [f(x) - g(x)] \, dx, \quad \bar{y} = \frac{1}{2A} \int_{a}^{b} \left([f(x)]^2 - [g(x)]^2\right) \, dx$$
These formulas find the geometric center of balance $(\bar{x}, \bar{y})$ of a flat plate of uniform density bounded by two curves. The x-coordinate averages the first moment of area divided by total area $A$, and the y-coordinate averages the vertical midpoints of the strips.

---

## 19. Hydrostatic Force on a Submerged Vertical Plate
$$F = \rho g \int_{a}^{b} y \cdot w(y) \, dy$$
This equation calculates the total fluid pressure force pushing against a submerged vertical dam or wall. The pressure increases linearly with depth $y$ ($\rho g y$), which is multiplied by the plate's width $w(y)$ and integrated over the submerged depth from $a$ to $b$.

---

## 20. Improper Integral with Infinite Upper Bound
$$\int_{a}^{\infty} f(x) \, dx = \lim_{t \to \infty} \int_{a}^{t} f(x) \, dx$$
An improper integral with an infinite limit evaluates the area under an unbounded curve. You integrate up to a finite cutoff variable $t$ and then take the limit as $t$ approaches infinity. If the limit exists as a finite number, the integral converges; otherwise, it diverges.

---

## 21. Improper p-Integral Convergence Condition
$$\int_{1}^{\infty} \frac{1}{x^p} \, dx \text{ converges } \iff p > 1$$
The improper p-integral test provides a benchmark for convergence. When the power $p > 1$, the function drops toward zero fast enough that the total infinite area under the curve remains finite (equal to $\frac{1}{p-1}$). When $p \le 1$, the area is infinite and diverges.

---

## 22. Separable First-Order Differential Equation
$$\frac{dy}{dx} = g(x)h(y) \implies \int \frac{1}{h(y)} \, dy = \int g(x) \, dx$$
A first-order differential equation is separable if the derivative factors into an isolated function of $x$ multiplied by a function of $y$. You separate all $y$-terms with $dy$ on the left side and all $x$-terms with $dx$ on the right side, and then integrate both sides independently.

---

## 23. Standard Form of First-Order Linear ODE
$$\frac{dy}{dx} + P(x) y = Q(x)$$
This is the standard formulation for a first-order linear ordinary differential equation. The unknown function $y$ and its derivative appear to the first power and are multiplied only by coefficient functions of the independent variable $x$.

---

## 24. Integrating Factor for Linear First-Order ODE
$$I(x) = e^{\int P(x) \, dx}$$
The integrating factor $I(x)$ is a multiplier that transforms the left-hand side of a linear differential equation into the exact derivative of a single product $\frac{d}{dx}[I(x)y]$. Multiplying the entire equation by $I(x)$ allows direct integration.

---

## 25. General Solution of First-Order Linear ODE
$$y(x) = \frac{1}{I(x)} \left( \int I(x) Q(x) \, dx + C \right)$$
This closed-form formula gives the complete general solution to any first-order linear differential equation. After multiplying $Q(x)$ by the integrating factor $I(x)$ and integrating, you divide the entire result by $I(x)$, which distributes the constant $C$.

---

## 26. Logistic Differential Equation
$$\frac{dP}{dt} = k P \left(1 - \frac{P}{M}\right)$$
The logistic equation models population growth with a finite environmental carrying capacity $M$. When the population $P$ is small, growth is nearly exponential at rate $k$. As $P$ approaches $M$, the factor $(1 - P/M)$ approaches zero, causing growth to smoothly level off.

---

## 27. Logistic Population Growth Function
$$P(t) = \frac{M}{1 + A e^{-kt}}$$
This S-shaped (sigmoid) curve is the explicit solution to the logistic differential equation. The parameter $A = \frac{M - P_0}{P_0}$ is set by the initial population $P_0$. The curve features an inflection point at half of the carrying capacity ($P = M/2$), where growth rate reaches its peak.

---

## 28. Parametric Derivative (Slope of Tangent)
$$\frac{dy}{dx} = \frac{\frac{dy}{dt}}{\frac{dx}{dt}} \quad \left(\frac{dx}{dt} \ne 0\right)$$
When a curve is defined parametrically with both coordinates varying with time $t$ ($x(t), y(t)$), the tangent slope $\frac{dy}{dx}$ is calculated by dividing the vertical velocity $\frac{dy}{dt}$ by the horizontal velocity $\frac{dx}{dt}$.

---

## 29. Second Derivative in Parametric Form
$$\frac{d^2 y}{dx^2} = \frac{\frac{d}{dt}\left[\frac{dy}{dx}\right]}{\frac{dx}{dt}}$$
To find the concavity of a parametric curve, you take the time derivative of the first derivative $\frac{dy}{dx}$ and divide it again by $\frac{dx}{dt}$. A common mistake is simply dividing the second time derivatives $\frac{d^2y/dt^2}{d^2x/dt^2}$, which is mathematically incorrect.

---

## 30. Arc Length of a Parametric Curve
$$L = \int_{\alpha}^{\beta} \sqrt{\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2} \, dt$$
This formula computes the total distance traveled along a parametric path between times $t = \alpha$ and $t = \beta$. The expression inside the radical represents the instantaneous speed $\sqrt{(x')^2 + (y')^2}$; integrating speed over time yields the total path length.

---

## 31. Polar to Cartesian Coordinate Transformations
$$x = r \cos \theta, \quad y = r \sin \theta, \quad r^2 = x^2 + y^2$$
These transformation equations convert coordinates between polar form (radius $r$ and angle $\theta$) and standard rectangular Cartesian coordinates $(x, y)$. They are derived directly from right-triangle trigonometry on the unit circle.

---

## 32. Slope of Tangent Line in Polar Coordinates
$$\frac{dy}{dx} = \frac{r'(\theta) \sin \theta + r(\theta) \cos \theta}{r'(\theta) \cos \theta - r(\theta) \sin \theta}$$
This formula calculates the slope of the tangent line to a polar curve $r = f(\theta)$. It applies the parametric derivative rule by treating $x(\theta) = r(\theta)\cos\theta$ and $y(\theta) = r(\theta)\sin\theta$ as parametric functions and applying the product rule.

---

## 33. Area in Polar Coordinates
$$A = \frac{1}{2} \int_{\alpha}^{\beta} [r(\theta)]^2 \, d\theta$$
This formula computes the area swept out by a polar curve $r = f(\theta)$ between rays $\theta = \alpha$ and $\theta = \beta$. It sums infinitesimal triangular wedges, each with area $\frac{1}{2} r^2 d\theta$, analogous to slices of a pie.

---

## 34. Arc Length of a Polar Curve
$$L = \int_{\alpha}^{\beta} \sqrt{[r(\theta)]^2 + [r'(\theta)]^2} \, d\theta$$
This formula calculates the length of a curve defined by a polar equation $r = f(\theta)$. It is obtained by simplifying the parametric arc length formula using the Pythagorean identity $\cos^2\theta + \sin^2\theta = 1$.

---

## 35. Divergence Test for Series (nth Term Test)
$$\lim_{n \to \infty} a_n \ne 0 \implies \sum_{n=1}^{\infty} a_n \text{ diverges}$$
The divergence test states that for an infinite series to have any hope of converging, its individual terms $a_n$ must shrink to zero. If the limit of $a_n$ is not zero (or does not exist), the sum immediately diverges. Note that the converse is not true: terms shrinking to zero does not guarantee convergence.

---

## 36. Integral Test for Infinite Series Convergence
$$\sum_{n=1}^{\infty} a_n \text{ converges } \iff \int_{1}^{\infty} f(x) \, dx < \infty$$
If $f(x)$ is a positive, continuous, and decreasing function matching terms $a_n = f(n)$, the infinite series and the improper integral converge or diverge together. This allows series convergence questions to be answered using standard integration.

---

## 37. p-Series Convergence Condition
$$\sum_{n=1}^{\infty} \frac{1}{n^p} \text{ converges } \iff p > 1$$
A p-series $\sum \frac{1}{n^p}$ converges if and only if the exponent $p$ is strictly greater than 1. When $p = 1$, it forms the famous Harmonic Series $\sum \frac{1}{n}$, which diverges to infinity even though its terms approach zero.

---

## 38. Direct Comparison Test
$$0 \le a_n \le b_n \land \sum b_n < \infty \implies \sum a_n < \infty$$
The direct comparison test determines convergence by comparing unknown positive terms $a_n$ against known benchmark terms $b_n$. If the terms are term-by-term smaller than a convergent series, the unknown series must converge; if larger than a divergent series, it must diverge.

---

## 39. Limit Comparison Test
$$\lim_{n \to \infty} \frac{a_n}{b_n} = L \in (0, \infty) \implies \left(\sum a_n \text{ and } \sum b_n \text{ both converge or diverge}\right)$$
When direct term-by-term inequalities are difficult to establish, the limit comparison test compares the long-term ratio $\frac{a_n}{b_n}$. If the ratio approaches a positive finite number $L$, both series share the exact same convergence behavior.

---

## 40. Alternating Series Test (Leibniz Criterion)
$$b_{n+1} \le b_n \land \lim_{n \to \infty} b_n = 0 \implies \sum_{n=1}^{\infty} (-1)^{n-1} b_n \text{ converges}$$
An alternating series whose terms alternate in sign converges if the magnitudes $b_n$ decrease monotonically ($b_{n+1} \le b_n$) and approach zero as $n \to \infty$. This guarantees convergence even when the absolute series diverges, as with the Alternating Harmonic Series.

---

## 41. Alternating Series Estimation Theorem (Remainder Bound)
$$|R_n| = |S - S_n| \le b_{n+1}$$
When approximating the sum of an alternating series with its first $n$ terms $S_n$, the maximum possible error (remainder $|R_n|$) is strictly less than or equal to the magnitude of the very next unused term $b_{n+1}$. This provides an easy error bound for numerical computations.

---

## 42. Ratio Test for Absolute Convergence
$$L = \lim_{n \to \infty} \left|\frac{a_{n+1}}{a_n}\right| < 1 \implies \sum a_n \text{ converges absolutely}$$
The ratio test evaluates the limiting growth ratio between consecutive terms. If $L < 1$, the terms shrink faster than a convergent geometric series, proving absolute convergence. If $L > 1$, the series diverges; if $L = 1$, the test is inconclusive and another test must be used.

---

## 43. Root Test for Series Convergence
$$L = \lim_{n \to \infty} \sqrt[n]{|a_n|} < 1 \implies \sum a_n \text{ converges absolutely}$$
The root test examines the limit of the $n$-th root of the absolute terms. It is especially effective when series terms involve entire expressions raised to the $n$-th power ($a_n = [u_n]^n$). If $L < 1$, the series converges absolutely.

---

## 44. General Form of a Power Series
$$\sum_{n=0}^{\infty} c_n (x - a)^n = c_0 + c_1(x - a) + c_2(x - a)^2 + \cdots$$
A power series is an infinite polynomial centered at $x = a$ with coefficients $c_n$. It acts as a continuous function on its interval of convergence, allowing complex non-elementary functions to be integrated, differentiated, and evaluated easily.

---

## 45. Radius of Convergence via Ratio Test
$$R = \lim_{n \to \infty} \left|\frac{c_n}{c_{n+1}}\right|$$
The radius of convergence $R$ defines a symmetric interval $(a - R, a + R)$ within which the power series converges absolutely. Inside this radius, the series can be differentiated and integrated term by term.

---

## 46. Taylor Series Expansion at a Point a
$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!} (x - a)^n$$
A Taylor series represents an infinitely differentiable function $f(x)$ as an infinite sum of polynomial terms calculated from its derivatives evaluated at a center point $a$. It is the theoretical backbone of scientific computing and function approximation.

---

## 47. Maclaurin Series Expansion (Taylor at Zero)
$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(0)}{n!} x^n$$
A Maclaurin series is the special case of a Taylor series centered at zero ($a = 0$). It expresses functions as infinite polynomials with powers of $x$, matching the function's value and all higher-order derivatives at the origin.

---

## 48. Maclaurin Series for Exponential Function
$$e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots$$
This infinite series represents the exponential function $e^x$ and converges for every real and complex number ($R = \infty$). It is used in software algorithms and microprocessors to evaluate exponential functions with arbitrary precision.

---

## 49. Maclaurin Series for Sine
$$\sin x = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots$$
The Maclaurin series for $\sin x$ contains only odd powers of $x$ with alternating signs, reflecting that sine is an odd symmetric function ($\sin(-x) = -\sin x$). It converges for all real numbers $x \in (-\infty, \infty)$.

---

## 50. Maclaurin Series for Cosine
$$\cos x = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots$$
The Maclaurin series for $\cos x$ contains only even powers of $x$ with alternating signs, reflecting that cosine is an even symmetric function ($\cos(-x) = \cos x$). Differentiating this series term by term yields the negative of the sine series.
