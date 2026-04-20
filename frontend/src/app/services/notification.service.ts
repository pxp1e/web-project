import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { ApiService } from './api.service';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private countSubject = new BehaviorSubject<number>(0);
  count$ = this.countSubject.asObservable();
  private interval: any = null;

  constructor(private api: ApiService, private auth: AuthService) {
    this.auth.user$.subscribe(user => {
      if (user) {
        this.start();
      } else {
        this.stop();
      }
    });
  }

  start(): void {
    this.loadCount();
    if (!this.interval) {
      this.interval = setInterval(() => this.loadCount(), 5000);
    }
  }

  stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.countSubject.next(0);
  }

  loadCount(): void {
    this.api.getNotificationCount().subscribe({
      next: (res) => this.countSubject.next(res.count),
      error: () => {}
    });
  }

  setCount(count: number): void {
    this.countSubject.next(count);
  }
}