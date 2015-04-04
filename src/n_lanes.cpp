/**
  Lucas Walter
  April 2015

  GPL 3.0

  

  g++ n_lanes.cpp -lopencv_highgui -lopencv_core && ./a.out


*/

#include <iostream>
#include <opencv2/highgui/highgui.hpp>
#include <vector>

class Lane
{
public:
  Lane(float y, float width);

  void draw(cv::Mat& im);
  float y_;
  float width_;

};

Lane::Lane(float y, float width) :
    y_(y),
    width_(width)
{
  std::cout << "Lane " << y_ << " " << width_ << std::endl;
}

void Lane::draw(cv::Mat& im)
{
  cv::Scalar col = cv::Scalar(30, 240, 240);
  for (int i = -1; i <= 1; i += 2)
  {
    cv::Point2f pt1 = cv::Point2f(0, y_ + i * width_/2.0);
    cv::Point2f pt2 = cv::Point2f(im.cols, y_ + i * width_/2.0);
    cv::line(im, pt1, pt2, col, 4);
  }

  const int font_face = cv::FONT_HERSHEY_SIMPLEX;
  const int thickness = 1;
  const double font_scale = 1.0;
  const int line_type = 8;

  cv::putText(im, "lane", cv::Point2f(50, y_ + width_/4.0),
      font_face, font_scale,
      col, thickness, line_type);

}

/////////////////////////////////////////////////////////////////
class Car
{
public:
  Car(cv::Point2f pos, cv::Point2f vel, cv::Point2f sz);
  
  void update(const float dt);
  void draw(cv::Mat& im);

  cv::Point2f pos_;
  cv::Point2f vel_;
  cv::Point2f sz_;

};

Car::Car(cv::Point2f pos, cv::Point2f vel, cv::Point2f sz) :
    pos_(pos),
    vel_(vel),
    sz_(sz)
{
  std::cout << "Car " << pos_ << vel_ << sz_ << std::endl;
}

void Car::update(const float dt)
{
  pos_ += vel_ * dt;

}

void Car::draw(cv::Mat& im)
{
  cv::Rect ob = cv::Rect(pos_ - sz_ * 0.5, pos_ + sz_ * 0.5);
  //std::cout << ob.width << " " << ob.x << std::endl; 
  cv::Scalar col(228, 220, 120);
  cv::rectangle(im, ob, col, 2, 2);
}

int main(int argn, char** argv)
{
  cv::Mat im = cv::Mat(cv::Size(1280,720), CV_8UC3, cv::Scalar::all(5));

  const float pix_per_foot = 5.0;
  const float width = pix_per_foot * 11;
  const float y = im.rows/2.0 + width/2.0;
  std::vector<Lane*> lanes;
  for (size_t i = 0; i < 2; ++i)
  {
    lanes.push_back(new Lane(y + i * width, width));
  }

  cv::Point2f car_sz(width * 1.5, width * 0.8);
  std::vector<Car*> cars;
  const int num_cars = 10;
  for (size_t i = 0; i < num_cars; ++i)
  {
    cv::Point2f pos(rand() % im.cols, y);
    const float vel_x = (5.0 * 5280.0 / (60.0 * 60.0)) * pix_per_foot;
    cv::Point2f vel(vel_x, 0);
    cars.push_back(new Car(pos, vel, car_sz)); 
  }

  const float dt = 1.0/30.0;
  while (true)
  {
    im = cv::Scalar::all(5);
    for (size_t i = 0; i < cars.size(); ++i)
    {
      cars[i]->update(dt);
      cars[i]->draw(im);
    }
    for (size_t i = 0; i < lanes.size(); ++i)
    {
      lanes[i]->draw(im);
    }

    cv::imshow("n_lanes", im);
    int key = cv::waitKey(50);
    if (key == 'q') break;
  
  }
}

