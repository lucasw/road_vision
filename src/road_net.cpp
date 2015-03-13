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
  cv::Point2f ap = start_->pos_;
  cv::Point2f bp = end_->pos_;
  cv::Point2f mid = ap + (bp - ap) * 0.8; 
  cv::line(image, ap, mid, col_, 1); 
  cv::line(image, mid, bp, col_ * 0.7, 1); 
}

int main(int argn, char** argv)
{
  const int wd = 1400;
  const int ht = 900;
  
  cv::Mat image = cv::Mat(cv::Size(wd, ht), CV_8UC3, cv::Scalar::all(0));

  std::vector<Node*> all_nodes;
  std::vector<Edge*> all_edges;

  const float div = 150.0;
  const float off = 20.0;
  const int x_num = float(wd)/div - 1;
  const int y_num = float(ht)/div - 1;
  for (size_t j = 0; j < y_num; ++j)
  {
    for (size_t i = 0; i < x_num; ++i)
    {
      // create an intersection
      const float x = i * div + div/2.0;
      const float y = j * div + div/2.0;
      all_nodes.push_back(new Node(cv::Point2f(x, y))); 
      
      if (i > 0)
      { 
        // to the west
        size_t ind1 = j * x_num * 4 + i * 4; //all_nodes.size() - 1;
        size_t ind2 = j * x_num * 4 + (i - 1) * 4 + 1;
        std::cout << "edge " << ind1 << " " << ind2 
            << " " << all_nodes.size() << std::endl;
        cv::Scalar col = cv::Scalar(255, 100, 50);
        all_edges.push_back(new Edge(all_nodes[ind1], all_nodes[ind2], col));
      }

      all_nodes.push_back(new Node(cv::Point2f(x + off, y)));

      if (false) // ((j > 1))
      {
        // to the north
        size_t ind = j * (x_num - 1) + i;
        size_t ind2 = (j - 1) * (x_num - 1) + i + 1;
        cv::Scalar col = cv::Scalar(255, 100, 90);
        all_edges.push_back(new Edge(all_nodes[ind], all_nodes[ind2], col));
      }

      all_nodes.push_back(new Node(cv::Point2f(x + off, y + off))); 
      all_nodes.push_back(new Node(cv::Point2f(x, y + off))); 
    
      if (false) //(i > 1)
      { 
        // to the west
        size_t ind = all_nodes.size() - 1;
        cv::Scalar col = cv::Scalar(120, 255, 50);
        all_edges.push_back(new Edge(all_nodes[ind], all_nodes[ind - 5], col));
      }
  
    }
  }
  std::cout << x_num << " " << y_num << " " 
      << all_nodes.size() << " " << all_edges.size() << std::endl;

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

