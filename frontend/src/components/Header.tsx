import React from 'react'
import Image from 'next/image'
import logo from '../../public/images/logo.png'

function Header() {
  return (
    <div className="flex sticky items-center h-20 z-10">
      <div className='flex items-center ml-10 rounded-lg'>
        <Image src={logo} alt='HCMUS icon' className='h-12 w-12'/>s
        <div className="flex items-center text-lg font-semibold text-blue-950">HCMUS Assistant</div>
      </div>
    </div>
  )
}

export default Header