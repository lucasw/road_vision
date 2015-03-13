/*
  Lucas Walter
  March 2015

  GPL 3.0

  
  Have a network of roads with cars moving along them

  g++ road_net.cpp -lopencv_highgui -lopencv_core && ./a.out
*/

#include <iostream>
#include <opencv2/highgui/highgui.hpp>
#include <map>
#include <vector>

// an intersection
class Node
{
public:
  Node(cv::Point2f pos);
  
  void draw(cv::Mat& image);

  std::vector<Node*> inputs_;
  std::vector<Node*> outputs_;
  
  cv::Point2f pos_;
};

Node::Node(cv::Point2f pos) :
    pos_(pos)
{
  
}
  
void Node::draw(cv::Mat& image)
{
  cv::Scalar col = cv::Scalar(255, 240, 10);
  cv::circle(image, pos_, 10, col); 
}

int main(int argn, char** argv)
{
  const int wd = 1400;
  const int ht = 900;
  
  cv::Mat image = cv::Mat(cv::Size(wd, ht), CV_8UC3, cv::Scalar::all(0));

  std::vector<Node*> all_nodes;

  const float div = 100.0;
  for (int j = div; j < ht - div; j += div)
  {
    for (int i = div; i < wd - div; i += div)
    {
      all_nodes.push_back(new Node(cv::Point2f(i, j))); 
    }
  }

  while (true) 
  {
    image = cv::Scalar::all(0);

    for (size_t i = 0; i < all_nodes.size(); ++i)
    {
      all_nodes[i]->draw(image);
    }
    
    cv::imshow("road network", image);
    const int key = cv::waitKey(20);
    if (key == 'q') break;
  }


}

