import React from 'react'
import thongtintuyensinh from '../../public/images/thongtintuyensinh.png'
import Image from 'next/image'

const Sidebar = () => {
  return (
    <div className='w-full p-3'>
        {/* Header */}
        <div className='w-full flex'>
            <Image src={thongtintuyensinh} alt='thong-tin-tuyen-sinh'/>
        </div>
    </div>
  )
}

export default Sidebar
