import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format } from "date-fns"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "PPP")
}

export function formatTime(date: string | Date): string {
  return format(new Date(date), "HH:mm")
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), "PPP • HH:mm")
}
