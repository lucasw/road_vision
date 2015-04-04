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
  std::cout << y_ << " " << width_ << std::endl;
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

  while (true)
  {
    im = cv::Scalar::all(5);
    for (size_t i = 0; i < lanes.size(); ++i)
    {
      lanes[i]->draw(im);
    }

    cv::imshow("n_lanes", im);
    int key = cv::waitKey(5);
    if (key == 'q') break;
  
  }
}

