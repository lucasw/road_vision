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

class Edge;
// an intersection
class Node
{
public:
  Node(cv::Point2f pos);
  
  void draw(cv::Mat& image);

  // TBD or just all connections mixed?
  std::vector<Edge*> inputs_;
  std::vector<Edge*> outputs_;
  
  const cv::Point2f pos_;
};

Node::Node(cv::Point2f pos) :
    pos_(pos)
{
   
}

void Node::draw(cv::Mat& image)
{
  cv::Scalar col = cv::Scalar(255, 240, 10);
  cv::circle(image, pos_, 4, col); 
}

class Edge
{
public:
  Edge(const Node* start, const Node* end, cv::Scalar col);
  
  void draw(cv::Mat& image);

  const Node* start_;
  const Node* end_;
  cv::Scalar col_;
};

Edge::Edge(const Node* start, const Node* end, const cv::Scalar col) :
    start_(start),
    end_(end),
    col_(col)
{
}

void Edge::draw(cv::Mat& image)
{
  cv::line(image, start_->pos_, end_->pos_, col_, 1); 
}

int main(int argn, char** argv)
{
  const int wd = 1400;
  const int ht = 900;
  
  cv::Mat image = cv::Mat(cv::Size(wd, ht), CV_8UC3, cv::Scalar::all(0));

  std::vector<Node*> all_nodes;
  std::vector<Edge*> all_edges;

  const float div = 200.0;
  const float off = 20.0;
  for (int j = div; j < ht - div; j += div)
  {
    for (int i = div; i < wd - div; i += div)
    {
      all_nodes.push_back(new Node(cv::Point2f(i, j))); 
      
      int ind = all_nodes.size() - 1;
      if ((i > div) && (i + div < wd))
      { 
        cv::Scalar col = cv::Scalar(255, 100, 50);
        all_edges.push_back(new Edge(all_nodes[ind - 3], all_nodes[ind], col));
      }

      all_nodes.push_back(new Node(cv::Point2f(i + off, j))); 
    
      all_nodes.push_back(new Node(cv::Point2f(i + off, j + off))); 
      
      all_nodes.push_back(new Node(cv::Point2f(i, j + off))); 
    
      ind = all_nodes.size() - 1;
      if ((i > div) && (i + div < wd))
      { 
        cv::Scalar col = cv::Scalar(120, 255, 50);
        all_edges.push_back(new Edge(all_nodes[ind], all_nodes[ind - 5], col));
      }


  
    }
  }

  while (true) 
  {
    image = cv::Scalar::all(0);

    for (size_t i = 0; i < all_nodes.size(); ++i)
    {
      all_nodes[i]->draw(image);
    }
    for (size_t i = 0; i < all_edges.size(); ++i)
    {
      all_edges[i]->draw(image);
    }
    
    cv::imshow("road network", image);
    const int key = cv::waitKey(20);
    if (key == 'q') break;
  }


}

