import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent) },
  { path: 'register', loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent) },
  { path: 'dashboard', loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent), canActivate: [AuthGuard] },
  { path: 'teams', loadComponent: () => import('./pages/teams/teams.component').then(m => m.TeamsComponent), canActivate: [AuthGuard] },
  { path: 'teams/:id', loadComponent: () => import('./pages/board/board.component').then(m => m.BoardComponent), canActivate: [AuthGuard] },
  { path: 'subjects', loadComponent: () => import('./pages/subjects/subjects.component').then(m => m.SubjectsComponent), canActivate: [AuthGuard] },
  { path: '**', redirectTo: '/dashboard' }
];