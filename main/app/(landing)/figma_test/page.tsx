'use client'
import React from 'react';
import Image from 'next/image';

export default function FigmaTest() {
  return (
    <div className="relative min-h-screen bg-white overflow-hidden">
      {/* Hero Section */}
      <div className="relative">
        {/* Background Decoration */}
        <div className="absolute top-0 right-0 w-2/3 h-[723px] bg-[#FFF9F5] z-0" />
        <div className="absolute top-0 left-0 w-1/3 h-[587px] bg-purple-100 opacity-30 rounded-full blur-[150px] z-0" />

        {/* Navigation */}
        <nav className="relative z-10 max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center">
            <div className="text-2xl font-bold">Jadoo</div>
            <div className="h-4 w-10 bg-[#F1A501] ml-2 rounded-sm" />
          </div>
          
          <div className="hidden md:flex space-x-8 text-[#212832] font-medium">
            <a href="#" className="hover:text-[#F1A501] transition">Destinations</a>
            <a href="#" className="hover:text-[#F1A501] transition">Hotels</a>
            <a href="#" className="hover:text-[#F1A501] transition">Flights</a>
            <a href="#" className="hover:text-[#F1A501] transition">Bookings</a>
            <a href="#" className="hover:text-[#F1A501] transition">Login</a>
            <a href="#" className="border border-[#212832] px-5 py-2 rounded-md hover:bg-[#212832] hover:text-white transition">Sign up</a>
            <div className="flex items-center">
              <span>EN</span>
              <svg className="w-2 h-2 ml-1" viewBox="0 0 8 4" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1L4 3L7 1" stroke="#212832" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 pt-10 pb-20 grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="flex flex-col justify-center">
            <p className="text-[#DF6951] font-bold uppercase tracking-wide mb-4">Best Destinations around the world</p>
            
            <div className="relative">
              <h1 className="text-5xl md:text-7xl font-bold text-[#181E4B] leading-tight mb-8">
                Travel, enjoy<br />
                and live a new<br />
                and full life
              </h1>
              <div className="absolute -bottom-4 left-0 w-3/4 h-3 bg-[#DF6951] opacity-30 rounded-full" />
            </div>
            
            <p className="text-[#5E6282] text-lg mb-8 max-w-lg">
              Built Wicket longer admire do barton vanity itself do in it. Preferred to sportsmen it engrossed listening. Park gate sell they west hard for the.
            </p>
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
              <button className="bg-gradient-to-b from-[#FF946D] to-[#FF7D68] text-white px-6 py-4 rounded-lg font-semibold shadow-lg shadow-[#FF7D68]/20 hover:shadow-xl hover:shadow-[#FF7D68]/30 transition">
                Find out more
              </button>
              
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-14 h-14 bg-[#DF6951] rounded-full flex items-center justify-center shadow-lg shadow-[#DF6951]/30">
                    <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-white border-b-[6px] border-b-transparent ml-1" />
                  </div>
                </div>
                <span className="text-[#686D77] font-medium">Play Demo</span>
              </div>
            </div>
          </div>
          
          <div className="relative flex items-center justify-center">
            <div className="relative w-full h-[500px]">
              <Image 
                src="https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/7f12f500-2b2a-4e4e-8ba2-a6b19f43c35d" 
                alt="Traveler with airplane" 
                fill
                style={{ objectFit: 'contain' }}
                priority
              />
            </div>
            
            {/* Decorative elements */}
            <div className="absolute top-1/4 right-1/4 animate-bounce-slow">
              <div className="relative w-16 h-16 bg-gradient-to-br from-[#747DEF] to-[#5E3BE1] rounded-full flex items-center justify-center transform rotate-[-30deg]">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscribe Section */}
      <div className="relative max-w-7xl mx-auto px-4 py-20">
        <div className="relative bg-[#DFD7F9]/20 rounded-tl-[20px] rounded-br-[20px] rounded-tr-[129px] rounded-bl-[20px] p-16">
          {/* Decorative circles */}
          <div className="absolute top-0 right-0 opacity-10">
            <div className="relative">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div 
                  key={i} 
                  className="absolute border border-[#6246E5] rounded-full"
                  style={{
                    width: `${i * 40}px`,
                    height: `${i * 40}px`,
                    top: `-${i * 10}px`,
                    right: `-${i * 10}px`,
                  }}
                />
              ))}
            </div>
          </div>
          
          <div className="text-center max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-semibold text-[#5E6282] mb-16">
              Subscribe to get information, latest news and other interesting offers about Jadoo
            </h2>
            
            <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
              <div className="relative w-full md:w-auto flex-1 max-w-md">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                  <svg width="21" height="18" viewBox="0 0 21 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="0.5" y="0.5" width="20" height="17" rx="4.5" stroke="#39425D"/>
                    <path d="M5 9H17" stroke="#39425D" strokeLinecap="round"/>
                  </svg>
                </div>
                <input 
                  type="email" 
                  placeholder="Your email" 
                  className="w-full py-4 px-12 rounded-lg text-[#39425D] focus:outline-none focus:ring-2 focus:ring-[#FF7D68]/50"
                />
              </div>
              
              <button className="w-full md:w-auto whitespace-nowrap bg-gradient-to-b from-[#FF946D] to-[#FF7D68] text-white px-6 py-4 rounded-lg font-semibold">
                Subscribe
              </button>
            </div>
          </div>
          
          {/* Send icon decoration */}
          <div className="absolute -top-8 right-16">
            <div className="relative w-16 h-16 bg-gradient-to-br from-[#747DEF] to-[#5E3BE1] rounded-full flex items-center justify-center transform rotate-[-30deg]">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
        
        {/* Decorative plus signs */}
        <div className="absolute right-0 top-1/4 grid grid-cols-3 gap-4 opacity-30">
          {Array(15).fill('+').map((_, i) => (
            <span key={i} className={`text-2xl ${i === 4 ? 'text-[#6246E5]' : 'text-gray-400'} ${i === 12 ? 'text-[#FF7D68]' : ''}`}>+</span>
          ))}
        </div>
      </div>

      <style jsx global>{`
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(-5%);
            animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
          }
          50% {
            transform: translateY(0);
            animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 3s infinite;
        }
      `}</style>
    </div>
  );
}
