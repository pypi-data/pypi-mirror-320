#include "Clothoids.hh"
#include "GenericContainer/GenericContainer.hh"
#include <string>
#include <utility>
#include <vector>

namespace clothoids
{

class ClothoidCurve
{
private:
  G2lib::ClothoidCurve clothoid_curve;

public:
  ClothoidCurve(std::string const &name = "") : clothoid_curve{name} {}

  ClothoidCurve(double x0, double y0, double theta0, double k, double dk, double L, std::string const &name)
      : clothoid_curve{x0, y0, theta0, k, dk, L, name}
  {
  }

  void build(double x0, double y0, double theta0, double k, double dk, double L)
  {
    this->clothoid_curve.build(x0, y0, theta0, k, dk, L);
  }

  int build_G1(double x0, double y0, double theta0, double x1, double y1, double theta1, double tol = 1e-12)
  {
    return this->clothoid_curve.build_G1(x0, y0, theta0, x1, y1, theta1, tol);
  }

  double length() { return this->clothoid_curve.length(); }

  std::pair<double, double> eval(double s)
  {
    double x, y;
    this->clothoid_curve.eval(s, x, y);
    return {x, y};
  }

  std::pair<double, double> curvature_min_max()
  {
    double kappa_min, kappa_max;
    this->clothoid_curve.curvature_min_max(kappa_min, kappa_max);
    return {kappa_min, kappa_max};
  }

  double theta(double s) { return this->clothoid_curve.theta(s); }

  double theta_D(double s) { return this->clothoid_curve.theta_D(s); }

  double theta_DD(double s) { return this->clothoid_curve.theta_DD(s); }

  double theta_DDD(double s) { return this->clothoid_curve.theta_DDD(s); }

  void set_gc(GC_namespace::GenericContainer &gc) { gc.dump(std::cout); }

  GC_namespace::GenericContainer get_gc()
  {
    GC_namespace::GenericContainer gc;
    gc["string"] = "Hello";
    gc["int"]    = 42;
    return gc;
  }
};

class ClothoidList
{
private:
  G2lib::ClothoidList clothoid_list;

public:
  ClothoidList(std::string const &name = "") : clothoid_list{name} {}

  bool build_G1(std::vector<double> const &x, std::vector<double> const &y)
  {
    return this->clothoid_list.build_G1(x.size(), x.data(), y.data());
  }

  bool
  build_G1(std::vector<double> const &x, std::vector<double> const &y, std::vector<double> const &theta)
  {
    return this->clothoid_list.build_G1(x.size(), x.data(), y.data(), theta.data());
  }

  bool build(
    const double &x0, const double &y0, const double &theta0, std::vector<double> const &s, std::vector<double> const &kappa
  )
  {
    return this->clothoid_list.build(x0, y0, theta0, s, kappa);
  }

  double length() { return this->clothoid_list.length(); }

  std::pair<double, double> eval(const double &s)
  {
    double x, y;
    this->clothoid_list.eval(s, x, y);
    return {x, y};
  }

  std::pair<std::vector<double>, std::vector<double>> eval(std::vector<double> const &s)
  {
    std::vector<double> x, y;
    x.reserve(s.size());
    y.reserve(s.size());
    for (size_t i{0}; i <= s.size(); i++)
    {
      double _x, _y;
      this->clothoid_list.eval(s[i], _x, _y);
      x.push_back(_x);
      y.push_back(_y);
    }

    return std::make_pair(std::move(x), std::move(y));
  }

  std::vector<double> evaluate(const double &s)
  {
    double theta, kappa, x, y;
    this->clothoid_list.evaluate(s, theta, kappa, x, y);
    return {theta, kappa, x, y};
  }

  double theta(const double &s)
  {
    double theta;
    theta = this->clothoid_list.theta(s);
    return theta;
  }

  double theta_D(const double &s)
  {
    double theta_D;
    theta_D = this->clothoid_list.theta_D(s);
    return theta_D;
  }

  std::pair<double, double> findST1(const double &x, const double &y)
  {
    double s, n; // curvilinear abscissa and lateral coordinate
    this->clothoid_list.findST1(x, y, s, n);
    return {s, n};
  }
};

}; // namespace clothoids
