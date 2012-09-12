#include <cstdlib>
#include <fstream>
using namespace std;

/*
  bonk.cc altered to use USACO-style FILE I/O (bonk.in, bonk.out).
  
  Command line: ../mini-grader.py ./usaco.exe --task=bonk --usaco
  
  Test cases:

  1: Passed
  2: Wrong answer
  3: Time limit
  4: Memory limit (heap)
  5: Memory limit (stack)
  6: Memory limit (heap+stack)
  7: Passed (alloc + free)
  8: Runtime error (abort())
 */

static int checksum(const char *bytes, int size, int result=0) {
  for (int i=0; i<int(size); ++i) {
    result += bytes[i];
  }
  return result;
}

static char *heap_alloc(size_t size) {
  char *chunk = new char[size]; // 1 MB
  for (int i=0; i<int(size); ++i) {
    chunk[i] = i+3;
  }
  return chunk;
}

#include <stdint.h>
static int stack_alloc(int iter, size_t size) {
  if (iter <= 0) {
    return 0;
  }
  char chunk[size];
  for (int i=0; i<int(size); ++i) {
    chunk[i] = i+3;
  }
  int result = stack_alloc(iter-1, size);
  return checksum(chunk, size, result);
}

int main() {
  ifstream fin("bonk.in");
  ofstream fout("bonk.out");
  int testno;
  fin >> testno;

  switch (testno) {
  case 1:
    fout << 2*testno << "\n";
    break;

  case 2:
    fout << 3*testno << "\n";
    break;

  case 3:
    {
      long long acc = 0;
      for (long long i=0; i<1000000000000LL; ++i) {
        acc += i;
      }
      fout << acc << "\n";
    }
    break;

  case 4:
    // Try to allocate 1 GB on the heap
    for (int iter=0; iter<1024; ++iter) {
      heap_alloc(1<<20);
    }
    break;

  case 5:
    // Try to allocate 1 GB on the stack
    stack_alloc(1024, 1<<20);
    break;

  case 6:
    // Allocate 200 MB on heap and 200 MB on stack
    heap_alloc(200 * (1<<20));
    stack_alloc(200, 1<<20);
    break;

  case 7:
    // Allocate 100 MB on heap, free, 100 on stack, then heap again
    {
      int result = 0;
      char *chunk;
      chunk = heap_alloc(100 * (1<<20));
      result += checksum(chunk, 100 * (1<<20));
      delete[] chunk;
      result += stack_alloc(100, (1<<20));
      chunk = heap_alloc(100 * (1<<20));
      result += checksum(chunk, 100 * (1<<20));
      delete[] chunk;
    }
    fout << 2*testno << "\n";
    break;

  case 8:
    abort();
  }

  return 0;
}
