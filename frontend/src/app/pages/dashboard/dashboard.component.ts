import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { DashboardStats } from '../../models/dashboard.model';
import { Task } from '../../models/task.model';
import { User } from '../../models/user.model';
import { NavbarComponent } from '../../components/navbar/navbar';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, NavbarComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  stats: DashboardStats | null = null;
  myTasks: Task[] = [];
  user: User | null = null;
  loading = true;
  error = '';

  constructor(private api: ApiService, private auth: AuthService, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.user = this.auth['userSubject'].getValue();
    this.loadData();
  }

  loadData(): void {
    this.api.getStats().subscribe({
      next: (s) => { this.stats = s; this.cdr.detectChanges(); },
      error: () => { this.error = 'Failed to load stats'; }
    });

    this.api.getMyTasks().subscribe({
      next: (t) => { this.myTasks = t; this.loading = false; this.cdr.detectChanges(); },
      error: () => { this.error = 'Failed to load tasks'; this.loading = false; }
    });
  }

  logout(): void {
    this.auth.logout();
  }

  getPriorityClass(p: string): string {
    return `priority-${p}`;
  }

  goToTask(task: any): void {
  this.router.navigate(['/teams', task.team], {
    queryParams: { taskId: task.id }
  });
}
}