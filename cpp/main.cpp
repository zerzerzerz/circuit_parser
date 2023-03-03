#include<iostream>
#include<vector>
using namespace std;

const int maxN = 1e5+10;
vector<int> color(maxN, 0) , pre(maxN, 0), adj[maxN];

vector<vector<int> > res;

void build_cycle(int start, int end) {
  vector<int> cycle;
  cycle.push_back(start);
  for (int cur = end; cur != start; cur = pre[cur]) {
    cycle.push_back(cur);
  }
  cycle.push_back(start);

  vector<int> reversedCycle;
  for (int i = cycle.size() - 1; i >= 0; i--) {
    reversedCycle.push_back(cycle[i]);
  }

  res.push_back(reversedCycle);
}

void dfs(int source) {
  color[source] = 1;
  for (int &target: adj[source]) {
    if (color[target] == 0) {
      pre[target] = source;
      dfs(target);
    } else if (color[target] == 1) {
      build_cycle(target, source);
    }
  }
  color[source] = 2;
}

int main() {
  int n, m;
  cin >> n >> m;
  while (m--) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
  }

  for (int i = 1; i <= n; i++) {
    if (color[i] == 0) {
      dfs(i);
    }
  }

  if (res.size() != 0) {
    for (int i = 0; i < res.size(); i++) {
      cout << res[i].size() << endl;
      for (int j = 0; j < res[i].size(); j++) {
        cout << res[i][j] << " ";
      }
      cout << endl;
    }
  } else {
    cout << "IMPOSSIBLE" << endl;
  }

  return 0;
}