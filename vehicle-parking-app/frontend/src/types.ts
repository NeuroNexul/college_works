export interface ParkingSpot {
  id: number
  lot_id: number
  status: 'Available' | 'Occupied'
}

export interface ParkingLot {
  id: number
  name: string
  address: string
  pin_code: string
  price_per_hour: number
  total_spots: number
  occupied_spots_count: number
  spots: ParkingSpot[]
}

export interface Booking {
  id: number
  booking_time: string // ISO 8601 string
  parking_time: string | null // ISO 8601 string
  release_time: string | null // null if the booking is currently active
  total_cost: number | null // null if active
  vehicle_number: string
  spot: {
    id: number
  }
  lot: {
    id: number
    name: string
    address: string
  }
}

export interface RegisteredUser {
  id: number
  email: string
  fullName: string | null
  role?: 'User' | 'Admin'
  address: string | null
  pinCode: string | null

  totalBookings: number
  activeBookings: number
  totalSpent: number
}

export interface UserSummaryData {
  kpis: {
    totalSessions: number
    totalSpent: number
    avgCost: number
  }
  favoriteLot: {
    name: string
    visits: number
  }
  monthlySpending: { month: string; total: number }[]
  dayOfWeekParking: Record<string, number> // e.g., { "Mon": 5, "Tue": 3, ... }
}

export interface AdminSummaryData {
  kpis: {
    totalLots: number
    totalUsers: number
    totalSpots: number
    liveOccupancyPercent: number
    totalRevenue: number
  }
  dailyRevenue: { day: string; total: number }[]
  topLots: { id: number; name: string; booking_count: number }[]
  occupancyByLot: { name: string; occupied: number; available: number }[]
}
