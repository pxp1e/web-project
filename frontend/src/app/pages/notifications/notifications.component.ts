import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { NavbarComponent } from '../../components/navbar/navbar';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, RouterLink, NavbarComponent],
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css']
})
export class NotificationsComponent implements OnInit {
  notifications: any[] = [];
  loading = true;

  constructor(
    private api: ApiService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private notifService: NotificationService
  ) {}

  ngOnInit(): void {
    this.api.getNotifications().subscribe({
      next: (n) => {
        this.notifications = n;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.loading = false; }
    });
  }

  openNotification(notification: any): void {
    this.api.markOneRead(notification.id).subscribe({
      next: () => {
        this.notifications = this.notifications.map(n =>
          n.id === notification.id ? { ...n, is_read: true } : n
        );
        this.notifService.setCount(this.getUnreadCount());
        this.cdr.detectChanges();
        if (notification.team_id) {
          this.router.navigate(['/teams', notification.team_id], {
            queryParams: { taskId: notification.task_id }
          });
        }
      }
    });
  }

  getUnreadCount(): number {
    return this.notifications.filter(n => !n.is_read).length;
  }

  markAllRead(): void {
    this.api.markAllRead().subscribe({
      next: () => {
        this.notifications = this.notifications.map(n => ({ ...n, is_read: true }));
        this.notifService.setCount(0);
        this.cdr.detectChanges();
      }
    });
  }
}