import org.springframework.beans.factory.annotation.Autowired;

class Unsafe {
  @Autowired
  Service service;

  void run() {
    System.out.println("debug");
  }
}

class Service {}
